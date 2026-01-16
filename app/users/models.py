from sqlalchemy import Column, Integer, String, Date, DateTime, Table, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

# Association table for many-to-many relationship between User and Role
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
)


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

    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Verification code for phone verification
    verification_code = Column(String(6), nullable=True)
    verification_code_expires = Column(DateTime(timezone=True), nullable=True)

    # Password reset token
    password_reset_token = Column(String(255), nullable=True, index=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)

    # Relationship to roles (many-to-many)
    roles = relationship("Role", secondary=user_roles, back_populates="users")

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


class Role(Base):
    """
    Represents the roles table
    """
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    
    # Role name (e.g., "admin", "healthcare_professional", "patient", etc.)
    name = Column(String(50), unique=True, nullable=False, index=True)
    
    # Role display name (e.g., "Healthcare Professional")
    display_name = Column(String(100), nullable=False)
    
    # Description of the role
    description = Column(String(255), nullable=True)
    
    # Whether this is a system role (cannot be deleted)
    is_system_role = Column(Boolean, default=False, nullable=False)
    
    # Whether the role is active
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationship to users (many-to-many)
    users = relationship("User", secondary=user_roles, back_populates="roles")
    
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