human_handoff_detect_prompt = """
As an assistant, analyze the conversation history between agent and user, and determine if human service is needed.
agent is responsible for scheduling appointments for medical service.

Conversation History:
    {conversation_history}
"""
