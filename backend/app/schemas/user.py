"""User schemas"""

from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for creating a user"""

    username: str
    email: EmailStr
    hashed_password: str
    first_name: str = None
    last_name: str = None


class UserResponse(BaseModel):
    """Schema for user response"""

    id: int
    username: str
    email: str
    first_name: str = None
    last_name: str = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
