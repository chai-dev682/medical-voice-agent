from langchain_community.chat_message_histories import ChatMessageHistory
from typing import Optional
from datetime import datetime

from app.schemas.appointment import Appointment
from app.core.logger import logger
from app.core.prompt_templates.extract_appointment_info import extract_appointment_info_prompt
from app.core.prompt_templates.extract_rescheduled_appointment_info import extract_rescheduled_appointment_info_prompt
from app.utils.function_call import function_call
from app.utils.utils import format_conversation_history, get_current_datetime
from app.services.twilio_sms import SMSService
from app.services.oystehr import OystehrService

class AppointmentService:
    def __init__(self):
        self.sms_service = SMSService()
        self.oystehr_service = OystehrService()

    def extract_appointment_details(self, conversation_history: ChatMessageHistory) -> Optional[Appointment]:
        """Extract appointment details from conversation text using OpenAI function calling."""
        try:
            extracted_info = function_call(extract_appointment_info_prompt.format(conversation_history=format_conversation_history(conversation_history), current_datetime=get_current_datetime()), "extract_appointment_info")

            # Extract the function call arguments
            if extracted_info["has_appointment_info"]:
                # Parse the datetime
                date_time_str = f"{extracted_info["appointment_details"]["appointment_date"]} {extracted_info["appointment_details"]["appointment_time"]}"
                appointment_datetime = datetime.strptime(date_time_str, "%Y-%m-%d %I:%M %p")

                # Create and return the appointment
                return Appointment(
                    patient_name=extracted_info["appointment_details"]["patient_name"],
                    phone_number=extracted_info["appointment_details"]["phone_number"].replace("-", " "),
                    datetime=appointment_datetime
                )
            
            return None

        except Exception as e:
            logger.error(f"Error extracting appointment details: {e}")
            return None
    
    def extract_rescheduled_appointment_info(self, conversation_history: ChatMessageHistory):
        """Extract patient name and rescheduled appointment date and time from conversation text using OpenAI function calling."""
        try:
            extracted_info = function_call(extract_rescheduled_appointment_info_prompt.format(conversation_history=format_conversation_history(conversation_history), current_datetime=get_current_datetime()), "extract_rescheduled_appointment_info")
            return extracted_info
        except Exception as e:
            logger.error(f"Error extracting name: {e}")
            return None
    
    async def schedule_appointment(self, conversation_history: ChatMessageHistory):
        logger.info(f"Scheduling appointment...")
        appointment = self.extract_appointment_details(conversation_history)
        
        if appointment:
            try:
                # Create appointment in Oystehr
                if await self.oystehr_service.create_appointment(appointment):
                    # Format and send SMS confirmation
                    appointment_details = self.format_appointment_details(appointment)
                    await self.sms_service.send_confirmation(
                        appointment.phone_number,
                        appointment_details
                    )
                    logger.info(f"SMS confirmation sent to {appointment.phone_number}")
                    return True
                return False
            except Exception as e:
                logger.error(f"Error in appointment scheduling workflow: {e}")
                return False
        else:
            logger.info("No appointment details could be extracted from conversation")
            return False

    @staticmethod
    def format_appointment_details(appointment: Appointment) -> str:
        """Format appointment details for SMS confirmation."""
        return (
            f"Appointment Details:\n"
            f"Patient: {appointment.patient_name}\n"
            f"Date: {appointment.datetime.strftime('%B %d, %Y')}\n"
            f"Time: {appointment.datetime.strftime('%I:%M %p')}\n"
        )

    async def reschedule_appointment(self, conversation_history: ChatMessageHistory):
        """Handle appointment rescheduling workflow."""
        logger.info("Processing rescheduling request...")
        
        # Extract patient name and rescheduled appointment date and time
        rescheduled_appointment_info = self.extract_rescheduled_appointment_info(conversation_history)
        if not rescheduled_appointment_info:
            logger.error("Could not extract patient name and rescheduled appointment date and time")
            return False

        try:
            # Search for existing patient
            patient = await self.oystehr_service.search_patient(rescheduled_appointment_info["name"])
            if not patient:
                logger.error("Could not find existing patient for rescheduling")
                return False

            # Get existing appointment
            existing_appointment = await self.oystehr_service.search_appointment(patient["id"])
            if not existing_appointment:
                logger.error("Could not find existing appointment for rescheduling")
                return False

            # Update the appointment in Oystehr
            new_appointment = Appointment(
                patient_name=patient["name"][0]["text"],
                phone_number="not needed for rescheduling",
                datetime=datetime.strptime(f"{rescheduled_appointment_info["rescheduled_appointment_date"]} {rescheduled_appointment_info["rescheduled_appointment_time"]}", "%Y-%m-%d %I:%M %p"),
                notes=f"Rescheduled from {existing_appointment['planningHorizon']['start']}"
            )
            if await self.oystehr_service.update_appointment(existing_appointment["id"], patient["id"], new_appointment):
                # Send SMS confirmation
                appointment_details = self.format_appointment_details(new_appointment)
                await self.sms_service.send_confirmation(
                    new_appointment.phone_number,
                    f"Your appointment has been rescheduled:\n{appointment_details}"
                )
                logger.info(f"Rescheduling confirmation sent to {new_appointment.phone_number}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error in rescheduling workflow: {e}")
            return False
