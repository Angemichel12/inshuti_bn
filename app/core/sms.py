import requests
from typing import Optional
from app.core.config import settings
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


def send_sms(to: str, text: str, sender: str = "PindoTest") -> bool:
    """
    Send SMS using Pindo API
    
    Args:
        to: Phone number in E.164 format (e.g., +250781234567)
        text: Message text
        sender: Sender name (default: "Pindo")
    
    Returns:
        True if SMS sent successfully, False otherwise
    
    Raises:
        HTTPException: If SMS sending fails
    """
    if not settings.PINDO_TOKEN:
        logger.error("PINDO_TOKEN not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SMS service not configured"
        )
    
    token = settings.PINDO_TOKEN
    headers = {'Authorization': f'Bearer {token}'}
    data = {
        'to': to,
        'text': text,
        'sender': sender
    }
    url = 'https://api.pindo.io/v1/sms/'
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if response.status_code == 200:
            logger.info(f"SMS sent successfully to {to}")
            return True
        else:
            logger.error(f"Failed to send SMS: {result}")
            print(f"Failed to send SMS: {result}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending SMS: {str(e)}")
        print(f"Error sending SMS: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send SMS: {str(e)}"
        )


def send_verification_code(phone_number: str, code: str) -> bool:
    """
    Send verification code via SMS
    
    Args:
        phone_number: Phone number in E.164 format
        code: Verification code (6 digits)
    
    Returns:
        True if sent successfully
    """
    message = f"Your verification code is: {code}. Valid for 10 minutes."
    return send_sms(phone_number, message)


def send_password_reset_code(phone_number: str, code: str) -> bool:
    """
    Send password reset code via SMS
    
    Args:
        phone_number: Phone number in E.164 format
        code: Reset code (6 digits)
    
    Returns:
        True if sent successfully
    """
    message = f"Your password reset code is: {code}. Valid for 15 minutes."
    return send_sms(phone_number, message)