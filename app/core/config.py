from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings - loaded from .env file
    """
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # SMS Configuration (Pindo)
    PINDO_TOKEN: Optional[str] = os.getenv("PINDO_TOKEN", None)
    SMS_SENDER_NAME: str = os.getenv("SMS_SENDER_NAME", "Pindo")
    
    # Verification Code Settings
    VERIFICATION_CODE_EXPIRE_MINUTES: int = 10
    PASSWORD_RESET_CODE_EXPIRE_MINUTES: int = 15
    
    # Application
    APP_NAME: str = "My FastAPI App"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create a single instance to use throughout the app
settings = Settings()