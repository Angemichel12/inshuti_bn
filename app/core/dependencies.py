from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.config import settings
from app.database import get_db
from app.users.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user_id = None
    
    try:
        # Decode the JWT token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Extract user_id from token (it will be a string)
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Convert string to integer
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTClaimsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation error: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        # For debugging - you can remove this in production
        if settings.DEBUG:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"JWT Error: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        raise credentials_exception
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Catch any other unexpected errors
        if settings.DEBUG:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication error: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        raise credentials_exception
    
    # Ensure user_id was successfully extracted
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not extract user ID from token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Query user from database (with roles loaded)
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User with ID {user_id} not found. The token may be invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def has_role(user: User, role_name: str) -> bool:
    """
    Check if a user has a specific role
    
    Args:
        user: User object
        role_name: Name of the role to check (case-insensitive)
    
    Returns:
        True if user has the role, False otherwise
    """
    if not user.roles:
        return False
    
    role_name_lower = role_name.lower()
    return any(role.name.lower() == role_name_lower and role.is_active for role in user.roles)


def require_role(role_name: str):
    """
    Dependency factory to require a specific role
    
    Usage:
        @router.get("/admin-only")
        def admin_endpoint(current_user: User = Depends(require_role("admin"))):
            ...
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if not has_role(current_user, role_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. This endpoint requires '{role_name}' role."
            )
        return current_user
    
    return role_checker


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to ensure the current user has admin role
    Use this for admin-only endpoints
    
    Usage:
        @router.post("/admin-endpoint")
        def admin_function(admin_user: User = Depends(get_admin_user)):
            ...
    """
    if not has_role(current_user, "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. This endpoint requires 'admin' role."
        )
    return current_user