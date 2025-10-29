"""
In-memory user storage for authentication.
In production, this should use a proper database.
"""

from typing import Optional, Dict
from app.models.schemas import UserInDB
from passlib.context import CryptContext


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# In-memory user database
# In production, this should be replaced with actual database storage
_users_db: Dict[str, UserInDB] = {
    # Default admin user
    "admin": UserInDB(
        username="admin",
        email="admin@example.com",
        full_name="System Administrator",
        role="admin",
        disabled=False,
        hashed_password=pwd_context.hash("admin123")  # Change in production!
    ),
    # Default candidate user
    "candidate": UserInDB(
        username="candidate",
        email="candidate@example.com",
        full_name="Test Candidate",
        role="candidate",
        disabled=False,
        hashed_password=pwd_context.hash("test123")
    )
}


def get_user(username: str) -> Optional[UserInDB]:
    """
    Retrieve a user by username.
    
    Args:
        username: Username to look up
        
    Returns:
        UserInDB object if found, None otherwise
    """
    return _users_db.get(username)


def create_user(username: str, password: str, email: Optional[str] = None, 
                full_name: Optional[str] = None, role: str = "candidate") -> UserInDB:
    """
    Create a new user.
    
    Args:
        username: Unique username
        password: Plain text password (will be hashed)
        email: Optional email address
        full_name: Optional full name
        role: User role (candidate or admin)
        
    Returns:
        Created UserInDB object
        
    Raises:
        ValueError: If username already exists
    """
    if username in _users_db:
        raise ValueError(f"Username '{username}' already exists")
    
    hashed_password = pwd_context.hash(password)
    user = UserInDB(
        username=username,
        email=email,
        full_name=full_name,
        role=role,
        disabled=False,
        hashed_password=hashed_password
    )
    
    _users_db[username] = user
    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """
    Authenticate a user by username and password.
    
    Args:
        username: Username
        password: Plain text password
        
    Returns:
        UserInDB object if authentication successful, None otherwise
    """
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if user.disabled:
        return None
    return user


def get_all_users() -> Dict[str, UserInDB]:
    """
    Get all users (admin only).
    
    Returns:
        Dictionary of all users
    """
    return _users_db.copy()


def delete_user(username: str) -> bool:
    """
    Delete a user (admin only).
    
    Args:
        username: Username to delete
        
    Returns:
        True if deleted, False if user not found
    """
    if username in _users_db:
        del _users_db[username]
        return True
    return False
