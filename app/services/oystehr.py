from datetime import timedelta
import requests

from app.core.config import settings
from app.core.logger import logger
from app.schemas.appointment import Appointment

class OystehrService:
    def __init__(self):
        self.base_url = settings.OYSTEHR_API_URL
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "authorization": f"Bearer {settings.OYSTEHR_AUTH_TOKEN}",
            "x-zapehr-project-id": settings.OYSTEHR_PROJECT_ID
        }

    async def create_appointment(self, appointment: Appointment) -> bool:
        """Create an appointment in Oystehr."""
        try:
            patient_id = await self.create_patient(appointment)
            if not patient_id:
                logger.error("Failed to create patient in Oystehr")
                return False

            payload = {
                "resourceType": "Schedule",
                "active": True,
                "actor": [
                    {
                        "reference": f"Patient/{patient_id}",
                        "display": appointment.patient_name
                    }
                ],
                "planningHorizon": {
                    "start": appointment.datetime.strftime("%Y-%m-%dT%H:%M:%S%zZ"),
                    "end": (appointment.datetime + timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%S%zZ")
                },
                "comment": appointment.notes
            }
            response = requests.post(
                f"{self.base_url}/Schedule",
                headers=self.headers,
                json=payload
            )
            
            data = response.json()
            if response.status_code != 201:
                logger.error(f"Error creating an appointment in Oystehr: {data}")
                return False

            logger.info(f"Oystehr appointment created: {data}")

            return True
        except Exception as e:
            logger.error(f"Error creating appointment in Oystehr: {e}")
            return False
    
    async def create_patient(self, appointment: Appointment):
        """Create a patient in Oystehr."""
        try:
            payload = {
                "resourceType": "Patient",
                "active": True,
                "name": [
                    {
                        "text": appointment.patient_name
                    }
                ],
                "telecom": [
                    {
                        "system": "phone",
                        "value": appointment.phone_number
                    }
                ]
            }
            response = requests.post(
                f"{self.base_url}/Patient",
                headers=self.headers,
                json=payload
            )
            data = response.json()

            if response.status_code != 201:
                logger.error(f"Error creating patient in Oystehr: {data}")
                return None

            logger.info(f"Oystehr patient created: {data}")

            return data["id"]
        except Exception as e:
            logger.error(f"Error creating patient in Oystehr: {e}")
            return None
    
    async def search_patient(self, name: str):
        """Search for a patient in Oystehr by name."""
        try:
            response = requests.get(
                f"{self.base_url}/Patient?name={name}",
                headers=self.headers
            )
            data = response.json()
            if response.status_code != 200:
                logger.error(f"Error searching for patient in Oystehr: {data}")
                return None
            
            logger.info(f"Oystehr patient search results: {data}")

            return data['entry'][0]['resource'] if data['total'] > 0 else None
        except Exception as e:
            logger.error(f"Error searching for patient in Oystehr: {e}")
            return None
    
    async def search_appointment(self, patient_id: str):
        """Search for an appointment in Oystehr by patient ID."""
        try:
            response = requests.get(
                f"{self.base_url}/Schedule?actor={patient_id}",
                headers=self.headers
            )
            data = response.json()
            if response.status_code != 200:
                logger.error(f"Error searching for appointment in Oystehr: {data}")
                return None
            
            logger.info(f"Oystehr appointment search results: {data}")

            return data['entry'][0]['resource'] if data['total'] > 0 else None
        except Exception as e:
            logger.error(f"Error searching for appointment in Oystehr: {e}")
            return None
    
    async def update_appointment(self, appointment_id: str, patient_id: str, appointment: Appointment):
        """Update an appointment in Oystehr."""
        try:
            payload = {
                "resourceType": "Schedule",
                "id": appointment_id,
                "active": True,
                "actor": [
                    {
                        "reference": f"Patient/{patient_id}",
                        "display": appointment.patient_name
                    }
                ],
                "planningHorizon": {
                    "start": appointment.datetime.strftime("%Y-%m-%dT%H:%M:%S%zZ"),
                    "end": (appointment.datetime + timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%S%zZ")
                },
                "comment": appointment.notes
            }
            response = requests.put(
                f"{self.base_url}/Schedule/{appointment_id}",
                headers=self.headers,
                json=payload
            )
            data = response.json()
            if response.status_code != 200:
                logger.error(f"Error updating appointment in Oystehr: {data}")
                return False

            logger.info(f"Oystehr appointment updated: {data}")

            return True
        except Exception as e:
            logger.error(f"Error updating appointment in Oystehr: {e}")
            return False