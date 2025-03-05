extract_appointment_info_prompt = """
You are a medical office assistant. Extract appointment details from the conversation.
appointment details include:
- patient name
- phone number
- appointment date and time
- appointment notes

The current date and time is:
    {current_datetime}

Conversation History:
    {conversation_history}

If the conversation history does not contain any appointment details, return None.
"""
