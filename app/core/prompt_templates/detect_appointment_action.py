detect_appointment_action_prompt = """
As an AI assistant, analyze the conversation to determine if this is a new appointment request, a rescheduling request, or requires human handoff.

Key Detection Criteria:
1. Rescheduling Request:
   - Mentions of changing existing appointment
   - References to previous/current appointment
   - Words like "reschedule", "change", "move", "switch"
   - Mentions of being unable to make current appointment time

2. Human Handoff Required:
   - Medical emergencies or urgent symptoms
   - Complex medical questions beyond scheduling
   - Aggressive or distressed patients
   - Technical issues
   - Requests for medical advice
   - Explicit requests for human staff

3. New Appointment:
   - First-time appointment requests
   - No mention of existing appointments
   - General scheduling inquiries

Conversation History:
{conversation_history}

Determine the appropriate action based on the conversation content.
Remember: Only use human handoff when absolutely necessary. In most cases, you can simply tell the user to schedule or reschedule.
"""