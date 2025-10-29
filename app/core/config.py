from pydantic import  AnyHttpUrl
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME:str='TranscriptApplication'
    DEBUG:bool=False
    GOOGLE_API_KEY:str
    SENTRY_DNS:str| None=None
    ALLOWED_HOSTS:list[str]=["*"]
    DATABASE_URL:str
    NEBIUS_API_KEYS:str
    

    class Config:
        env_file = ".env"

settings=Settings()