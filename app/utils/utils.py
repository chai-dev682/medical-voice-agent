from langchain_community.chat_message_histories import ChatMessageHistory
from datetime import datetime

def format_conversation_history(messages: ChatMessageHistory) -> str:
    return "\n".join([f"{msg.type}: {msg.content}" for msg in messages.messages])

def get_current_datetime():
    now = datetime.now()
    return f"date: {now.strftime('%Y-%m-%d')}, time: {now.strftime('%I:%M %p')}"
