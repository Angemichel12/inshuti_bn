
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings - loaded from .env file
    """
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application
    APP_NAME: str = "My FastAPI App"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

# Create a single instance to use throughout the app
settings = Settings()