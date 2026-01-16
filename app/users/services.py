from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from app.users import models, schemas
from app.core.security import hash_password, verify_password, generate_verification_code, generate_reset_token
from fastapi import HTTPException, status
from typing import List, Optional
from app.core.sms import send_verification_code, send_password_reset_code
from app.core.config import settings



def create_user(db: Session, user_data: schemas.UserCreate):
    """
    Create a new user and send verification code via SMS
    
    Raises:
        HTTPException: If phone number already exists or other database error occurs
    """
    # Check if phone number already exists
    existing_user = db.query(models.User).filter(
        models.User.phone_number == user_data.phone_number
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with phone number {user_data.phone_number} already exists"
        )
    
    hashed_password = hash_password(user_data.password)
    
    # Generate verification code
    verification_code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=settings.VERIFICATION_CODE_EXPIRE_MINUTES)

    user = models.User(
        full_name=user_data.full_name,
        phone_number=user_data.phone_number,
        gender=user_data.gender,
        birth_date=user_data.birth_date,
        password=hashed_password,
        verification_code=verification_code,
        verification_code_expires=expires_at,
        is_active=True,
        is_verified=False
    )

    try:
        db.add(user)
        db.flush()  # Flush to get user.id
        
        # Assign default role (Patient) if no roles specified
        if not user_data.role_names:
            user_data.role_names = ["patient"]
        
        # Assign roles to user
        assign_roles_to_user(db, user, user_data.role_names)
        
        db.commit()
        db.refresh(user)
        
        # Send verification code via SMS
        sms_sent = False
        try:
            send_verification_code(user_data.phone_number, verification_code)
            sms_sent = True
        except Exception as sms_error:
            # Log the error but don't fail user creation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send verification SMS to {user_data.phone_number}: {str(sms_error)}")
            # User can request a new code using /resend-verification endpoint
        
        return user
    except IntegrityError as e:
        db.rollback()
        error_message = str(e.orig) if hasattr(e, 'orig') else str(e)
        if "phone_number" in error_message.lower() or "unique" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with phone number {user_data.phone_number} already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user. Please check your input data."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating user: {str(e)}"
        )


def authenticate_user(db: Session, phone_number: str, password: str):
    """
    Authenticate a user by phone number and password
    
    Returns:
        User object if authentication successful, None otherwise
    """
    user = db.query(models.User).filter(models.User.phone_number == phone_number).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.password):
        return None
    
    return user


def get_user_by_phone(db: Session, phone_number: str):
    """
    Get a user by phone number
    """
    return db.query(models.User).filter(models.User.phone_number == phone_number).first()


# Role Service Functions
def get_role_by_name(db: Session, role_name: str) -> Optional[models.Role]:
    """
    Get a role by its name
    """
    return db.query(models.Role).filter(models.Role.name == role_name.lower()).first()


def get_role_by_id(db: Session, role_id: int) -> Optional[models.Role]:
    """
    Get a role by its ID
    """
    return db.query(models.Role).filter(models.Role.id == role_id).first()


def get_all_roles(db: Session, include_inactive: bool = False) -> List[models.Role]:
    """
    Get all roles
    
    Args:
        include_inactive: If True, includes inactive roles
    """
    query = db.query(models.Role)
    if not include_inactive:
        query = query.filter(models.Role.is_active == True)
    return query.all()


def create_role(db: Session, role_data: schemas.RoleCreate) -> models.Role:
    """
    Create a new role
    
    Raises:
        HTTPException: If role name already exists
    """
    # Check if role already exists
    existing_role = get_role_by_name(db, role_data.name)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role with name '{role_data.name}' already exists"
        )
    
    role = models.Role(
        name=role_data.name.lower(),  # Store as lowercase for consistency
        display_name=role_data.display_name,
        description=role_data.description,
        is_system_role=False,
        is_active=True
    )
    
    try:
        db.add(role)
        db.commit()
        db.refresh(role)
        return role
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role with name '{role_data.name}' already exists"
        )


def update_role(db: Session, role_id: int, role_data: schemas.RoleUpdate) -> models.Role:
    """
    Update a role
    
    Raises:
        HTTPException: If role not found or trying to modify system role
    """
    role = get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    if role.is_system_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify system roles"
        )
    
    if role_data.display_name is not None:
        role.display_name = role_data.display_name
    if role_data.description is not None:
        role.description = role_data.description
    if role_data.is_active is not None:
        role.is_active = role_data.is_active
    
    try:
        db.commit()
        db.refresh(role)
        return role
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating role: {str(e)}"
        )


def delete_role(db: Session, role_id: int):
    """
    Delete a role (soft delete by setting is_active=False)
    
    Raises:
        HTTPException: If role not found or is a system role
    """
    role = get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    if role.is_system_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete system roles"
        )
    
    # Soft delete
    role.is_active = False
    try:
        db.commit()
        return {"message": f"Role '{role.name}' has been deactivated"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting role: {str(e)}"
        )


def assign_roles_to_user(db: Session, user: models.User, role_names: List[str]):
    """
    Assign roles to a user
    
    Raises:
        HTTPException: If any role not found
    """
    roles_to_assign = []
    for role_name in role_names:
        role = get_role_by_name(db, role_name)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role '{role_name}' not found"
            )
        if not role.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role '{role_name}' is not active"
            )
        if role not in user.roles:
            roles_to_assign.append(role)
    
    user.roles.extend(roles_to_assign)
    db.flush()


def remove_roles_from_user(db: Session, user: models.User, role_names: List[str]):
    """
    Remove roles from a user
    
    Raises:
        HTTPException: If any role not found
    """
    roles_to_remove = []
    for role_name in role_names:
        role = get_role_by_name(db, role_name)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role '{role_name}' not found"
            )
        if role in user.roles:
            roles_to_remove.append(role)
    
    for role in roles_to_remove:
        user.roles.remove(role)
    db.flush()


def initialize_default_roles(db: Session):
    """
    Initialize default system roles if they don't exist
    This should be called on application startup
    """
    default_roles = [
        {"name": "admin", "display_name": "Administrator", "description": "System administrator with full access", "is_system_role": True},
        {"name": "healthcare_professional", "display_name": "Healthcare Professional", "description": "Medical professionals providing healthcare services", "is_system_role": True},
        {"name": "patient", "display_name": "Patient", "description": "Patient receiving healthcare services", "is_system_role": True},
        {"name": "caretaker", "display_name": "Care Taker", "description": "Person taking care of a patient", "is_system_role": True},
        {"name": "pharmacist", "display_name": "Pharmacist", "description": "Dispenses medications and provides pharmaceutical care", "is_system_role": True},
    ]
    
    for role_data in default_roles:
        existing_role = get_role_by_name(db, role_data["name"])
        if not existing_role:
            role = models.Role(
                name=role_data["name"],
                display_name=role_data["display_name"],
                description=role_data["description"],
                is_system_role=role_data["is_system_role"],
                is_active=True
            )
            db.add(role)
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error initializing default roles: {str(e)}")
        
def send_account_verification_code(db: Session, phone_number: str):
    """
    Generate and send verification code to user's phone
    
    Raises:
        HTTPException: If user not found or SMS sending fails
    """
    user = get_user_by_phone(db, phone_number)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already verified"
        )
    
    # Generate verification code
    code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=settings.VERIFICATION_CODE_EXPIRE_MINUTES)
    
    # Save code to user
    user.verification_code = code
    user.verification_code_expires = expires_at
    
    try:
        db.commit()
        # Send SMS
        send_verification_code(phone_number, code)
        return {"message": "Verification code sent successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification code: {str(e)}"
        )


def verify_account(db: Session, phone_number: str, verification_code: str):
    """
    Verify user account with verification code
    
    Raises:
        HTTPException: If code is invalid or expired
    """
    user = get_user_by_phone(db, phone_number)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already verified"
        )
    
    if not user.verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No verification code found. Please request a new one."
        )
    
    if user.verification_code != verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    if user.verification_code_expires and user.verification_code_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has expired. Please request a new one."
        )
    
    # Verify the account
    user.is_verified = True
    user.verification_code = None
    user.verification_code_expires = None
    
    try:
        db.commit()
        db.refresh(user)
        return {"message": "Account verified successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify account: {str(e)}"
        )


def request_password_reset(db: Session, phone_number: str):
    """
    Generate and send password reset code
    
    Raises:
        HTTPException: If user not found
    """
    user = get_user_by_phone(db, phone_number)
    if not user:
        # Don't reveal if user exists for security
        return {"message": "If the phone number exists, a reset code has been sent"}
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Generate reset code
    code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=settings.PASSWORD_RESET_CODE_EXPIRE_MINUTES)
    
    # Save reset code to user
    user.password_reset_token = code
    user.password_reset_expires = expires_at
    
    try:
        db.commit()
        # Send SMS
        send_password_reset_code(phone_number, code)
        return {"message": "If the phone number exists, a reset code has been sent"}
    except Exception as e:
        db.rollback()
        # Still return success message for security
        return {"message": "If the phone number exists, a reset code has been sent"}


def reset_password(db: Session, phone_number: str, reset_code: str, new_password: str):
    """
    Reset user password with reset code
    
    Raises:
        HTTPException: If code is invalid or expired
    """
    user = get_user_by_phone(db, phone_number)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.password_reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No reset code found. Please request a new one."
        )
    
    if user.password_reset_token != reset_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset code"
        )
    
    if user.password_reset_expires and user.password_reset_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset code has expired. Please request a new one."
        )
    
    # Reset password
    user.password = hash_password(new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    
    try:
        db.commit()
        return {"message": "Password reset successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset password: {str(e)}"
        )


def change_password(db: Session, user: models.User, current_password: str, new_password: str):
    """
    Change password for authenticated user
    
    Raises:
        HTTPException: If current password is incorrect
    """
    if not verify_password(current_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    user.password = hash_password(new_password)
    
    try:
        db.commit()
        return {"message": "Password changed successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )


# Update authenticate_user to check is_active and is_verified
def authenticate_user(db: Session, phone_number: str, password: str):
    """
    Authenticate a user by phone number and password
    
    Returns:
        User object if authentication successful, None otherwise
    """
    user = db.query(models.User).filter(models.User.phone_number == phone_number).first()
    
    if not user:
        return None
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact support."
        )
    
    if not verify_password(password, user.password):
        return None
    
    return user