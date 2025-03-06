extract_rescheduled_appointment_info_prompt = """
Extract the patient's name and rescheduled appointment date and time from the conversation history.

The current date and time is:
    {current_datetime}

Conversation History:
    {conversation_history}
"""