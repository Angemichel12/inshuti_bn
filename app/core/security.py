import bcrypt
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
import secrets
import string

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash a password
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Create a JWT access token
    
    Args:
        data: Dictionary containing the data to encode (should include 'sub' key with user_id)
        expires_delta: Optional timedelta for token expiration
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def generate_verification_code(length: int = 6) -> str:
    """
    Generate a random numeric verification code
    
    Args:
        length: Length of the code (default: 6)
    
    Returns:
        Random numeric code as string
    """
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def generate_reset_token() -> str:
    """
    Generate a secure random token for password reset
    
    Returns:
        Random token string
    """
    return secrets.token_urlsafe(32)