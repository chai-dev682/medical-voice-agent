import json

function_list = [
    {
        "type": "function",
        "function": {
            "name": "extract_appointment_info",
            "description": "Extract appointment information from conversation",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_name": {
                        "type": "string",
                        "description": "Full name of the patient"
                    },
                    "phone_number": {
                        "type": "string",
                        "description": "Patient's phone number (XXX-XXX-XXXX)"
                    },
                    "appointment_date": {
                        "type": "string",
                        "description": "Appointment date (YYYY-MM-DD)"
                    },
                    "appointment_time": {
                        "type": "string",
                        "description": "Appointment time (HH:MM AM/PM)"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Some notes about the appointment"
                    }
                },
                "required": ["patient_name", "phone_number", "appointment_date", "appointment_time", "notes"]
            }
        }
    }
]

functions = json.loads(json.dumps(function_list))
