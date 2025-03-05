from datetime import datetime
from enum import Enum
from pydantic import BaseModel

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class Appointment(BaseModel):
    patient_name: str
    phone_number: str
    datetime: datetime
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    notes: str | None = None
