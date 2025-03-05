from twilio.rest import Client
from app.core.config import settings
from app.core.logger import logger

class SMSService:
    def __init__(self):
        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )

    async def send_confirmation(
        self,
        to_number: str,
        appointment_details: str
    ) -> None:
        """Send appointment confirmation via SMS."""
        try:
            message = self.client.messages.create(
                body=f"Your appointment has been confirmed:\n{appointment_details}",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_number
            )
            logger.info(f"SMS sent successfully: {message.sid}")
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            raise
