"""
Authentication endpoints for user login and registration.
"""

from datetime import timedelta
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends

from app.core.security import create_access_token, get_current_user, get_current_admin
from app.core.config import settings
from app.models.schemas import Token, UserLogin, UserCreate, User
from app.db.users import authenticate_user, create_user, get_user, get_all_users


router = APIRouter()


@router.post("/auth/token", response_model=Token, tags=["Authentication"])
async def login(user_credentials: UserLogin):
    """
    Login with username and password to get JWT access token.
    
    **Default Users:**
    - **Admin**: username=`admin`, password=`admin123`
    - **Candidate**: username=`candidate`, password=`test123`
    
    **Example Request:**
    ```json
    {
      "username": "candidate",
      "password": "test123"
    }
    ```
    
    **Response:**
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer"
    }
    ```
    
    **How to use the token:**
    - Add to Authorization header: `Bearer <access_token>`
    - Token expires in 8 hours (480 minutes)
    """
    # Authenticate user
    user = authenticate_user(user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "email": user.email},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")


@router.post("/auth/register", response_model=User, tags=["Authentication"])
async def register_user(
    user_data: UserCreate,
    current_user: dict = Depends(get_current_admin)
):
    """
    Register a new user (Admin only).
    
    **⚠️ Admin Access Required**
    
    Only administrators can create new user accounts.
    Candidates cannot access this endpoint.
    
    **Example Request:**
    ```json
    {
      "username": "newuser",
      "password": "securepass123",
      "email": "user@example.com",
      "full_name": "John Doe",
      "role": "candidate"
    }
    ```
    
    **Roles:**
    - `candidate`: Regular user with read access to invoices
    - `admin`: Full access including user management
    
    **Response:**
    Returns the created user (without password).
    """
    try:
        # Create the user
        new_user = create_user(
            username=user_data.username,
            password=user_data.password,
            email=user_data.email,
            full_name=user_data.full_name,
            role=user_data.role
        )
        
        # Return user without password
        return User(
            username=new_user.username,
            email=new_user.email,
            full_name=new_user.full_name,
            role=new_user.role,
            disabled=new_user.disabled
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/auth/me", response_model=User, tags=["Authentication"])
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    **Requires:** Valid JWT token in Authorization header
    
    **Response:**
    Returns information about the currently authenticated user.
    """
    user_db = get_user(current_user.get("sub"))
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return User(
        username=user_db.username,
        email=user_db.email,
        full_name=user_db.full_name,
        role=user_db.role,
        disabled=user_db.disabled
    )


@router.get("/auth/users", response_model=List[User], tags=["Authentication"])
async def list_users(current_user: dict = Depends(get_current_admin)):
    """
    List all users (Admin only).
    
    **⚠️ Admin Access Required**
    
    Returns a list of all registered users.
    """
    users_db = get_all_users()
    users = [
        User(
            username=u.username,
            email=u.email,
            full_name=u.full_name,
            role=u.role,
            disabled=u.disabled
        )
        for u in users_db.values()
    ]
    return users


@router.get("/auth/verify", tags=["Authentication"])
async def verify_token_endpoint(current_user: dict = Depends(get_current_user)):
    """
    Verify if your JWT token is valid.
    
    **Requires:** Valid JWT token in Authorization header
    
    **Response:**
    Returns token validity and user information.
    """
    return {
        "valid": True,
        "username": current_user.get("sub"),
        "role": current_user.get("role"),
        "email": current_user.get("email"),
        "expires_at": current_user.get("exp")
    }
