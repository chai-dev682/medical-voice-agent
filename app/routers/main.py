import json
import traceback
from fastapi import APIRouter, Request, WebSocket
from fastapi.responses import HTMLResponse
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from twilio.twiml.voice_response import VoiceResponse, Connect
from elevenlabs import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from starlette.websockets import WebSocketDisconnect

from app.services.twilio_audio_interface import TwilioAudioInterface
from app.services.appointment import AppointmentService
from app.services.twilio_sms import SMSService
from app.core.config import settings
from app.core.logger import logger

router = APIRouter()

conversation_history = ChatMessageHistory()

# define services
sms_service = SMSService()
appointment_service = AppointmentService()

def handle_agent_response(text: str):
    conversation_history.add_ai_message(AIMessage(content=text))
    logger.info(f"Agent: {text}")

def handle_user_transcript(text: str):
    conversation_history.add_user_message(HumanMessage(content=text))
    logger.info(f"User: {text}")

async def schedule_appointment():
    logger.info(f"Scheduling appointment...")
    appointment = appointment_service.extract_appointment_details(conversation_history)
    
    if appointment:
        try:
            appointment_details = appointment_service.format_appointment_details(appointment)

            await sms_service.send_confirmation(
                appointment.phone_number,
                appointment_details
            )
            logger.info(f"SMS confirmation sent to {appointment.phone_number}")
        except Exception as e:
            logger.error(f"Error sending SMS confirmation: {e}")
    else:
        logger.info("No appointment details could be extracted from conversation")

@router.post("/twilio/inbound_call")
async def handle_incoming_call(request: Request):
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "Unknown")
    from_number = form_data.get("From", "Unknown")
    logger.info(f"Incoming call: CallSid={call_sid}, From={from_number}")

    # Clear conversation history for new call
    conversation_history.clear()

    response = VoiceResponse()
    connect = Connect()
    connect.stream(url=f"wss://{request.url.hostname}/media-stream")
    response.append(connect)
    return HTMLResponse(content=str(response), media_type="application/xml")

@router.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection opened")

    audio_interface = TwilioAudioInterface(websocket)
    eleven_labs_client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)

    try:
        conversation = Conversation(
            client=eleven_labs_client,
            agent_id=settings.ELEVENLABS_AGENT_ID,
            requires_auth=True, # Security > Enable authentication
            audio_interface=audio_interface,
            callback_agent_response=handle_agent_response,
            callback_user_transcript=handle_user_transcript,
        )

        conversation.start_session()
        logger.info("Conversation started")

        async for message in websocket.iter_text():
            if not message:
                continue
            data = json.loads(message)
            if data.get("event") == "stop" and "stop" in data:
                await schedule_appointment()
            await audio_interface.handle_twilio_message(data)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
        # Process conversation after disconnect
        await schedule_appointment()

    except Exception:
        logger.error("Error occurred in WebSocket handler:")
        traceback.print_exc()
    finally:
        try:
            conversation.end_session()
            conversation.wait_for_session_end()
            logger.info("Conversation ended")
        except Exception:
            logger.error("Error ending conversation session:")
            traceback.print_exc()