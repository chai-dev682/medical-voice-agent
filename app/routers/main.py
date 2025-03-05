import json
import traceback
from fastapi import APIRouter, Request, WebSocket
from fastapi.responses import HTMLResponse
from twilio.twiml.voice_response import VoiceResponse, Connect
from elevenlabs import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from starlette.websockets import WebSocketDisconnect

from app.services.twilio_audio_interface import TwilioAudioInterface
from app.core.config import settings
from app.core.logger import logger

router = APIRouter()

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

    try:
        conversation = Conversation(
            client=eleven_labs_client,
            agent_id=settings.ELEVENLABS_AGENT_ID,
            requires_auth=True, # Security > Enable authentication
            audio_interface=audio_interface,
            callback_agent_response=lambda text: logger.info(f"Agent: {text}"),
            callback_user_transcript=lambda text: logger.info(f"User: {text}"),
        )

        conversation.start_session()
        logger.info("Conversation started")

        async for message in websocket.iter_text():
            if not message:
                continue
            await audio_interface.handle_twilio_message(json.loads(message))

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception:
        logger.info("Error occurred in WebSocket handler:")
        traceback.logger.info_exc()
    finally:
        try:
            conversation.end_session()
            conversation.wait_for_session_end()
            logger.info("Conversation ended")
        except Exception:
            logger.info("Error ending conversation session:")
            traceback.logger.info_exc()
