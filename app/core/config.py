from enum import Enum
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # OpenAI settings
    OPENAI_API_KEY: str
    
    # Twilio settings
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str
    
    # ElevenLabs settings
    ELEVENLABS_API_KEY: str
    ELEVENLABS_AGENT_ID: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True

class ModelType(str, Enum):
    GPT4O = 'gpt-4o'
    GPT4O_MINI = 'gpt-4o-mini'
    GPT35 = 'gpt-3.5-turbo'

class ElevenlabsModelType(str, Enum):
    MULTILINGUAL_V2 = "eleven_multilingual_v2"
    FLASH_V2_5 = "eleven_flash_v2_5"
    TURBO_V2_5 = "eleven_turbo_v2_5"
    TURBO_V2 = "eleven_turbo_v2"
    FLASH_V2 = "eleven_flash_v2"
    MULTILINGUAL_STS_V2 = "eleven_multilingual_sts_v2"
    MULTILINGUAL_V1 = "eleven_multilingual_v1"
    ENGLISH_STS_V2 = "eleven_english_sts_v2"
    MONOLINGUAL_V1 = "eleven_monolingual_v1"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
