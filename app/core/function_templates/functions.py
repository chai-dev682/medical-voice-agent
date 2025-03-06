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
            "name": "extract_rescheduled_appointment_info",
            "description": "Extract the patient's name and rescheduled appointment date and time from the conversation history",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The patient's name"
                    },
                    "rescheduled_appointment_date": {
                        "type": "string",
                        "description": "Rescheduled appointment date (YYYY-MM-DD)"
                    },
                    "rescheduled_appointment_time": {
                        "type": "string",
                        "description": "Rescheduled appointment time (HH:MM AM/PM)"
                    },
                },
                "required": ["name", "rescheduled_appointment_date", "rescheduled_appointment_time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "detect_appointment_action",
            "description": "Determines if the conversation is about new appointment, rescheduling, or needs human handoff",
            "parameters": {
                "type": "object",
                "properties": {
                    "action_type": {
                        "type": "string",
                        "enum": ["new_appointment", "reschedule", "human_handoff"],
                        "description": "The type of action needed based on the conversation"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Explanation for the detected action type"
                    },
                    "existing_appointment_mentioned": {
                        "type": "boolean",
                        "description": "Whether an existing appointment was mentioned in the conversation"
                    }
                },
                "required": ["action_type", "reason", "existing_appointment_mentioned"]
            }
        }
    }
]

functions = json.loads(json.dumps(function_list))
