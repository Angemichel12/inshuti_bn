from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List


class UserCreate(BaseModel):
    """
    Schema for creating a new user
    """
    full_name: str = Field(..., example="Irving Nasri")

    phone_number: str = Field(
        ...,
        pattern=r"^\+[1-9]\d{7,14}$",
        example="+250788123456"
    )

    gender: str = Field(..., example="Male")

    birth_date: Optional[date] = Field(
        None,
        example="1998-05-21"
    )

    password: str = Field(..., min_length=8, example="StrongPassword123")
    
    # Optional: role names to assign during registration
    role_names: Optional[List[str]] = Field(
        None,
        example=["patient"]
    )


class UserResponse(BaseModel):
    """
    Schema for returning user data
    """
    id: int
    full_name: str
    phone_number: str
    gender: str
    birth_date: Optional[date]
    is_active: bool
    is_verified: bool
    roles: List["RoleResponse"] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """
    Schema for user login
    """
    phone_number: str = Field(
        ...,
        pattern=r"^\+[1-9]\d{7,14}$",
        example="+250788123456"
    )
    password: str = Field(..., min_length=1, example="StrongPassword123")


class Token(BaseModel):
    """
    Schema for JWT token response
    """
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Schema for token payload data
    """
    user_id: Optional[int] = None


# Verification Schemas
class VerifyAccountRequest(BaseModel):
    """
    Schema for account verification
    """
    phone_number: str = Field(
        ...,
        pattern=r"^\+[1-9]\d{7,14}$",
        example="+250788123456"
    )
    verification_code: str = Field(..., min_length=6, max_length=6, example="123456")


class ResendVerificationRequest(BaseModel):
    """
    Schema for resending verification code
    """
    phone_number: str = Field(
        ...,
        pattern=r"^\+[1-9]\d{7,14}$",
        example="+250788123456"
    )


# Password Reset Schemas
class ForgotPasswordRequest(BaseModel):
    """
    Schema for forgot password request
    """
    phone_number: str = Field(
        ...,
        pattern=r"^\+[1-9]\d{7,14}$",
        example="+250788123456"
    )


class ResetPasswordRequest(BaseModel):
    """
    Schema for password reset
    """
    phone_number: str = Field(
        ...,
        pattern=r"^\+[1-9]\d{7,14}$",
        example="+250788123456"
    )
    reset_code: str = Field(..., min_length=6, max_length=6, example="123456")
    new_password: str = Field(..., min_length=8, example="NewPassword123")


class ChangePasswordRequest(BaseModel):
    """
    Schema for changing password (when user is logged in)
    """
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)


# Response Schemas
class MessageResponse(BaseModel):
    """
    Generic message response
    """
    message: str
    success: bool = True


# Role Schemas
class RoleCreate(BaseModel):
    """
    Schema for creating a new role
    """
    name: str = Field(..., min_length=1, max_length=50, example="pharmacist")
    display_name: str = Field(..., min_length=1, max_length=100, example="Pharmacist")
    description: Optional[str] = Field(None, max_length=255, example="Dispenses medications and provides pharmaceutical care")


class RoleUpdate(BaseModel):
    """
    Schema for updating a role
    """
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


class RoleResponse(BaseModel):
    """
    Schema for returning role data
    """
    id: int
    name: str
    display_name: str
    description: Optional[str]
    is_system_role: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserRoleAssign(BaseModel):
    """
    Schema for assigning roles to a user
    """
    role_names: List[str] = Field(..., min_items=1, example=["patient", "caretaker"])


class UserRoleRemove(BaseModel):
    """
    Schema for removing roles from a user
    """
    role_names: List[str] = Field(..., min_items=1, example=["caretaker"])