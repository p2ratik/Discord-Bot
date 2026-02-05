from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Base user schema"""
    user_id: str
    username: str


class UserCreate(BaseModel):
    """Schema for creating a user"""
    user_id: str
    username: str


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    username: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user API responses"""
    id: int
    user_id: str
    username: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserWithRoles(UserResponse):
    """Schema for user with role data"""
    role: Optional[dict] = None
