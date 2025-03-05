from langchain_community.chat_message_histories import ChatMessageHistory
from typing import Optional
from datetime import datetime

from app.schemas.appointment import Appointment
from app.core.logger import logger
from app.core.prompt_templates.extract_appointment_info import extract_appointment_info_prompt
from app.utils.function_call import function_call

def get_current_datetime():
    now = datetime.now()
    return f"date: {now.strftime('%Y-%m-%d')}, time: {now.strftime('%I:%M %p')}"

def format_conversation_history(messages: ChatMessageHistory) -> str:
    return "\n".join([f"{msg.type}: {msg.content}" for msg in messages.messages])

class AppointmentService:
    def __init__(self):
        pass

    def extract_appointment_details(self, conversation_history: ChatMessageHistory) -> Optional[Appointment]:
        """Extract appointment details from conversation text using OpenAI function calling."""
        try:
            extracted_info = function_call(extract_appointment_info_prompt.format(conversation_history=format_conversation_history(conversation_history), current_datetime=get_current_datetime()), "extract_appointment_info")

            # Extract the function call arguments
            if extracted_info:                
                # Parse the datetime
                date_time_str = f"{extracted_info['appointment_date']} {extracted_info['appointment_time']}"
                appointment_datetime = datetime.strptime(date_time_str, "%Y-%m-%d %I:%M %p")

                # Create and return the appointment
                return Appointment(
                    patient_name=extracted_info['patient_name'],
                    phone_number=extracted_info['phone_number'].replace("-", " "),
                    datetime=appointment_datetime
                )
            
            return None

        except Exception as e:
            logger.error(f"Error extracting appointment details: {e}")
            return None

    @staticmethod
    def format_appointment_details(appointment: Appointment) -> str:
        """Format appointment details for SMS confirmation."""
        return (
            f"Appointment Details:\n"
            f"Patient: {appointment.patient_name}\n"
            f"Date: {appointment.datetime.strftime('%B %d, %Y')}\n"
            f"Time: {appointment.datetime.strftime('%I:%M %p')}\n"
        )
