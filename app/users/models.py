from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """
    Represents the users table
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Full name (e.g. "Irving Nasri")
    full_name = Column(String(100), nullable=False)

    # Phone number with country code (e.g. +250788123456)
    # E.164 max length = 15 characters
    phone_number = Column(String(15), unique=True, index=True, nullable=False)

    # Gender (Male / Female / Other)
    gender = Column(String(10), nullable=False)

    # Birth date (YYYY-MM-DD)
    birth_date = Column(Date, nullable=True)

    # Hashed password
    password = Column(String(255), nullable=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now()
    )
