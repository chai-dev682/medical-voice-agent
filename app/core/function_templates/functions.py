import json

function_list = [
    {
        "type": "function",
        "function": {
            "name": "extract_appointment_info",
            "description": "Extract appointment information from conversation if available, return None if no detailed appointment information is present",
            "parameters": {
                "type": "object",
                "properties": {
                    "has_appointment_info": {
                        "type": "boolean",
                        "description": "Whether the conversation contains detailed appointment information"
                    },
                    "appointment_details": {
                        "type": "object",
                        "description": "Detailed appointment information if available",
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
                        }
                    }
                },
                "required": ["has_appointment_info", "appointment_details"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "detect_human_handoff",
            "description": "Determines if text indicates a human handoff is needed",
            "parameters": {
                "type": "object",
                "properties": {
                    "is_human_handoff": {
                        "type": "boolean",
                        "description": "True if the text indicates a human handoff is needed"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Explanation of why this is or is not considered a human handoff"
                    }
                },
                "required": ["is_human_handoff", "reason"]
            }
        }
    }
]

functions = json.loads(json.dumps(function_list))
