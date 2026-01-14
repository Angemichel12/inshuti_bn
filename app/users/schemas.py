from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional


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


class UserResponse(BaseModel):
    """
    Schema for returning user data
    """
    id: int
    full_name: str
    phone_number: str
    gender: str
    birth_date: Optional[date]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
