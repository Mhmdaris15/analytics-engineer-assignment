"""
Security utilities for API authentication and authorization.
Implements Bearer Token (JWT) authentication with username/password.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token security scheme
security = HTTPBearer()

# JWT settings
SECRET_KEY = settings.secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing token payload (should include 'sub' with username)
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise credentials_exception from e


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Dependency to get the current authenticated user from Bearer token.
    
    This can be used as a dependency in route handlers to require authentication.
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        User information from token payload (username, role, etc.)
        
    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


async def get_current_admin(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Dependency to require admin role.
    
    Args:
        current_user: Current user from token
        
    Returns:
        User information if admin
        
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def verify_api_key_header(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> bool:
    """
    Dependency to verify JWT token from Bearer header.
    
    This validates JWT tokens for authenticated endpoints.
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        True if authenticated
        
    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    
    # Verify it's a valid JWT token
    try:
        payload = verify_token(token)
        return True
    except HTTPException:
        # If JWT verification fails, raise 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Optional dependency - only check if auth is enabled
async def optional_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[dict]:
    """
    Optional authentication dependency.
    
    Returns user info if authenticated, None otherwise.
    Useful for endpoints that work differently based on auth status.
    
    Args:
        credentials: Optional HTTP Authorization credentials
        
    Returns:
        User information or None
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = verify_token(token)
        return payload
    except HTTPException:
        return None
