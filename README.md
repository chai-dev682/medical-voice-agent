# AI-Powered Voice Agent for Medical Practice

## Overview

This project is a prototype for an AI-powered voice agent designed to handle incoming calls for a medical practice. It focuses on demonstrating the voice interaction workflow for appointment scheduling and management using advanced AI technologies.

## Core Features

### Voice Interaction
- Real-time voice conversations using ElevenLabs' conversational AI
- Natural language understanding and response generation
- Seamless voice-to-text and text-to-voice conversion

### Appointment Management
- New appointment scheduling
- Appointment rescheduling capability
- Intelligent conversation flow detection
- Integration with Oystehr EHR system
- Automated appointment confirmation via SMS

### Smart Routing
- Automated detection of conversation intent
- Intelligent human handoff for complex scenarios
- Warm transfer capability to human staff
- Conference call setup for smooth transitions

### EHR Integration
- Direct integration with Oystehr EHR system
- Patient record creation and lookup
- Appointment creation and updates
- Schedule management

## Technologies Used

### Core Services
- **ElevenLabs**: Voice generation and conversational AI
- **Twilio**: Call handling and SMS functionality
- **Oystehr**: EHR integration and appointment management
- **OpenAI**: Natural language processing and understanding

### Backend Stack
- FastAPI: Modern, fast web framework
- WebSocket: Real-time audio streaming
- Pydantic: Data validation
- Langchain: AI/LLM integration framework

## Setup Requirements

1. Clone the repository:
   ```bash
   git clone https://github.com/chai-dev682/medical-voice-agent.git
   cd medical-voice-agent
   ```

2. Create a virtual environment:
   ```bash
   python -m virtualenv venv
   source venv/bin/activate # On Windows: venv\Scripts\activate
   ```

3. Install Dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Application:
   ```bash
   python manage.py
   ```

5. Start ngrok tunnel:
   ```bash
   ┌──────────────────────────────────────────────────┐
   │  1. Install ngrok from https://ngrok.com         │
   │  2. Open terminal and run:                       │
   │     $ ngrok http 5000                            │
   │                                                  │
   │  📋 Copy the Forwarding URL:                     │
   │     https://[your-ngrok-subdomain].ngrok.app     │
   │     or                                           │
   │     https://[your-ngrok-subdomain].ngrok-free.app│
   └──────────────────────────────────────────────────┘
   ```

6. Configure Twilio:
   ```bash
   ┌──────────────────────────────────────────────────┐
   │  Update Twilio Webhook URL:                      │
   │  1. Go to Twilio Console                         │
   │  2. Find your phone number                       │
   │  3. Set Webhook URL to your ngrok URL            │
   └──────────────────────────────────────────────────┘
   ```

7. Call your Twilio phone number and test the application.

## Key Workflows

1. **New Appointment Scheduling**
   - Voice interaction for gathering patient details
   - Automatic appointment slot allocation
   - EHR record creation
   - SMS confirmation

2. **Appointment Rescheduling**
   - Existing appointment identification
   - Patient verification
   - New slot allocation
   - EHR record update
   - Confirmation notification

3. **Human Handoff**
   - Automatic detection of complex scenarios
   - Warm transfer to human staff
   - Conference call setup
   - Context preservation

## Project Structure

```
app/
├── core/
│   ├── config.py           # Configuration settings
│   ├── logger.py           # Logging setup
│   └── prompt_templates/   # AI prompt templates
├── routers/
│   └── main.py            # Main API routes
├── services/
│   ├── appointment.py      # Appointment management
│   ├── oystehr.py         # EHR integration
│   ├── twilio_sms.py      # SMS functionality
│   └── twilio_audio_interface.py # Audio handling
├── schemas/
│   └── appointment.py      # Data models
└── utils/                  # Utility functions
```

## Future Enhancements

- Advanced appointment availability checking
- Multi-language support
- Enhanced security measures
- Comprehensive logging and monitoring
- Additional EHR integrations
