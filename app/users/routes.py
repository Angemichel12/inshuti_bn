from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
from typing import List
from app.database import get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.core.dependencies import get_current_user, get_admin_user
from .models import User
from .schemas import (
    UserCreate, UserResponse, UserLogin, Token,
    RoleCreate, RoleUpdate, RoleResponse,
    UserRoleAssign, UserRoleRemove,
    VerifyAccountRequest, ResendVerificationRequest,
    ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest,
    MessageResponse
)
from .services import (
    create_user, authenticate_user,
    create_role, update_role, delete_role, get_all_roles, get_role_by_id,
    assign_roles_to_user, remove_roles_from_user,
    send_account_verification_code, verify_account,
    request_password_reset, reset_password, change_password
)

# Create a router for user-related endpoints
router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# User endpoints
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    
    Returns:
        UserResponse: Created user data
    
    Raises:
        HTTPException: 400 if phone number already exists
    """
    try:
        return create_user(db, user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.post("/login", response_model=Token)
def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login endpoint - authenticates user with phone_number and password
    Returns JWT access token
    """
    user = authenticate_user(db, user_credentials.phone_number, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's information
    Requires valid JWT token
    """
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a user by their ID
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


# Role Management Endpoints - Admin Only
@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_new_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    Create a new role
    Requires admin role
    """
    return create_role(db, role)


@router.get("/roles", response_model=List[RoleResponse])
def list_roles(
    include_inactive: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get all active roles (or all roles if include_inactive=True)
    Public endpoint - anyone can view roles
    """
    return get_all_roles(db, include_inactive=include_inactive)


@router.get("/roles/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a role by ID
    Public endpoint - anyone can view a role
    """
    from .services import get_role_by_id
    role = get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role


@router.put("/roles/{role_id}", response_model=RoleResponse)
def update_role_endpoint(
    role_id: int,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    Update a role
    Requires admin role
    """
    return update_role(db, role_id, role_data)


@router.delete("/roles/{role_id}")
def delete_role_endpoint(
    role_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    Delete (deactivate) a role
    Requires admin role
    """
    return delete_role(db, role_id)


@router.post("/{user_id}/roles", response_model=UserResponse)
def assign_user_roles(
    user_id: int,
    role_data: UserRoleAssign,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    Assign roles to a user
    Requires admin role
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        assign_roles_to_user(db, user, role_data.role_names)
        db.commit()
        db.refresh(user)
        return user
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error assigning roles: {str(e)}"
        )


@router.delete("/{user_id}/roles", response_model=UserResponse)
def remove_user_roles(
    user_id: int,
    role_data: UserRoleRemove,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    Remove roles from a user
    Requires admin role
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        remove_roles_from_user(db, user, role_data.role_names)
        db.commit()
        db.refresh(user)
        return user
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing roles: {str(e)}"
        )
router.post("/verify-account", response_model=MessageResponse)
def verify_user_account(
    verification_data: VerifyAccountRequest,
    db: Session = Depends(get_db)
):
    """
    Verify user account with verification code sent via SMS
    """
    return verify_account(db, verification_data.phone_number, verification_data.verification_code)


@router.post("/resend-verification", response_model=MessageResponse)
def resend_verification_code(
    request: ResendVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Resend verification code to user's phone
    """
    return send_account_verification_code(db, request.phone_number)


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset code via SMS
    """
    return request_password_reset(db, request.phone_number)


@router.post("/reset-password", response_model=MessageResponse)
def reset_user_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Reset password using reset code sent via SMS
    """
    return reset_password(db, request.phone_number, request.reset_code, request.new_password)


@router.post("/change-password", response_model=MessageResponse)
def change_user_password(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Change password for authenticated user
    Requires valid JWT token
    """
    return change_password(db, current_user, request.current_password, request.new_password)