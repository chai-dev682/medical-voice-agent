import json
import traceback
import asyncio
from fastapi import APIRouter, Request, WebSocket
from fastapi.responses import HTMLResponse
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from twilio.twiml.voice_response import VoiceResponse, Connect
from twilio.rest import Client
from elevenlabs import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from starlette.websockets import WebSocketDisconnect

from app.services.twilio_audio_interface import TwilioAudioInterface
from app.services.appointment import AppointmentService
from app.core.config import settings
from app.core.logger import logger
from app.utils.utils import format_conversation_history
from app.utils.function_call import function_call
from app.core.prompt_templates.detect_appointment_action import detect_appointment_action_prompt

router = APIRouter()

appointment_service = AppointmentService()

def handle_agent_response(conversation_history: ChatMessageHistory, text: str):
    conversation_history.add_ai_message(AIMessage(content=text))
    logger.info(f"Agent: {text}")

def handle_user_transcript(conversation_history: ChatMessageHistory, text: str):
    conversation_history.add_user_message(HumanMessage(content=text))
    logger.info(f"User: {text}")

async def warm_transfer_to_human_services(websocket: WebSocket):
    try:
        # Get the call SID from the websocket
        call_sid = getattr(websocket, "call_sid", None)
        if not call_sid:
            logger.error("Error: No call SID available for transfer")
            return
            
        # TODO: Inform the caller
        await websocket.send_json({
            "event": "message",
            "message": "We've detected a potential human service. Transferring you to a human. Please stay on the line."
        })
        
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        
        # Create a conference for the warm transfer
        conference_name = f"human_handoff_{call_sid}"
        
        # Update the call to join the conference
        client.calls(call_sid).update(
            twiml=f'<Response><Dial><Conference>{conference_name}</Conference></Dial></Response>'
        )
        
        # Get the emergency reason to send to medical services
        emergency_reason = getattr(websocket, "human_handoff_text", "Potential human handoff")
        
        # TODO: Configure this in your settings
        human_handoff_number = '+19095767898'
        
        # Create TwiML that first plays a message explaining the situation before joining the conference
        twiml = f"""
        <Response>
            <Say>This is an automated transfer from an AI assistant that has detected a potential human service.</Say>
            <Pause length="1"/>
            <Say>The caller reported: {emergency_reason}</Say>
            <Pause length="1"/>
            <Say>You will now be connected to the caller. Please provide assistance.</Say>
            <Dial>
                <Conference>{conference_name}</Conference>
            </Dial>
        </Response>
        """
        
        client.calls.create(
            to=human_handoff_number,
            from_=settings.TWILIO_PHONE_NUMBER,
            twiml=twiml
        )
        
        logger.info(f"Call transferred to human handoff. Conference: {conference_name}")
        
    except Exception as e:
        logger.info(f"Error transferring call to human handoff: {str(e)}")
        traceback.print_exc()

async def detect_conversation_action(conversation_history: ChatMessageHistory) -> dict:
    """Detect whether the conversation requires new appointment, rescheduling, or human handoff."""
    try:
        result = function_call(
            detect_appointment_action_prompt.format(
                conversation_history=format_conversation_history(conversation_history)
            ),
            "detect_appointment_action"
        )
        logger.info(f"Conversation action detected: {result['action_type']}")
        return result
    except Exception as e:
        logger.error(f"Error in conversation action detection: {str(e)}")
        traceback.print_exc()
        return {"action_type": "new_appointment", "reason": "Error in detection", "existing_appointment_mentioned": False}

@router.post("/twilio/inbound_call")
async def handle_incoming_call(request: Request):
    form_data = await request.form()
    call_sid = form_data.get("CallSid", "Unknown")
    from_number = form_data.get("From", "Unknown")
    logger.info(f"Incoming call: CallSid={call_sid}, From={from_number}")

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
    conversation_history = ChatMessageHistory()
    action_needed = {"human_handoff": False, "reschedule_requested": False}

    # Create a simpler callback that just checks and logs
    def user_followup_callback(conversation_history, websocket):
        def enhanced_callback(text):
            # Call the original callback
            handle_user_transcript(conversation_history, text)
            
            # Check conversation action
            action = asyncio.run(detect_conversation_action(conversation_history))
            
            if action["action_type"] == "human_handoff":
                logger.info(f"HUMAN HANDOFF DETECTED: {action['reason']}")
                action_needed["human_handoff"] = True
                websocket.human_handoff_text = action["reason"]
            elif action["action_type"] == "reschedule":
                logger.info(f"RESCHEDULE DETECTED: {action['reason']}")
                action_needed["reschedule_requested"] = True
                websocket.reschedule_reason = action["reason"]
        
        return enhanced_callback

    try:
        websocket.stream_sid = None
        websocket.human_handoff_text = None
        websocket.reschedule_reason = None

        conversation = Conversation(
            client=eleven_labs_client,
            agent_id=settings.ELEVENLABS_AGENT_ID,
            requires_auth=True, # Security > Enable authentication
            audio_interface=audio_interface,
            callback_agent_response=lambda text: handle_agent_response(conversation_history, text),
            callback_user_transcript=user_followup_callback(conversation_history, websocket),
        )

        conversation.start_session()
        logger.info("Conversation started")

        async for message in websocket.iter_text():
            if not message:
                continue
            try:
                data = json.loads(message)

                # Store the stream SID when it's received in the start event
                if data.get("event") == "start" and "start" in data:
                    websocket.stream_sid = data["start"].get("streamSid")
                    websocket.call_sid = data["start"].get("callSid")
                    logger.info(f"Stored stream SID: {websocket.stream_sid}")
                    logger.info(f"Stored call SID: {websocket.call_sid}")
                elif data.get("event") == "stop" and "stop" in data:
                    if action_needed["reschedule_requested"]:
                        await appointment_service.reschedule_appointment(conversation_history)
                    else:
                        await appointment_service.schedule_appointment(conversation_history)

                # Check for human handoff or handle the message
                if action_needed["human_handoff"]:
                    await warm_transfer_to_human_services(websocket)
                else:
                    await audio_interface.handle_twilio_message(data)
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                traceback.print_exc()

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
        # Process conversation after disconnect
        if not action_needed["human_handoff"]:
            await appointment_service.schedule_appointment(conversation_history)

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