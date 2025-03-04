from enum import Enum
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # OpenAI settings
    OPENAI_API_KEY: str
    # Twilio settings
    TWILIO_ACCOUNT_SID: str = None
    TWILIO_API_KEY: str = None
    TWILIO_API_SECRET: str = None
    TWILIO_NUMBER: str = None
    # ElevenLabs settings
    ELEVENLABS_API_KEY: str = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

class ModelType(str, Enum):
    gpt4o = 'gpt-4o'
    gpt4o_mini = 'gpt-4o-mini'
    embedding = 'text-embedding-ada-002'

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
