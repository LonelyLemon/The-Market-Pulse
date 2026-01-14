from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import (BaseModel, EmailStr, 
                      Field, field_validator)


class UserResponse(BaseModel):
    id: UUID
    username: str = Field(..., description="User's username")
    email: EmailStr = Field(..., description="User's email")
    is_verified: bool = Field(..., description="User's status (Verified=True/Unverified=False)")
    created_at: datetime = Field(..., description="Time of user creation")
    updated_at: datetime = Field(..., description="Latest user's update datetime")

class UserCreate(BaseModel):
    username: str = Field(..., description="User's username")
    email: EmailStr = Field(..., description="User's email")
    password: str

class UserUpdate(BaseModel):
    username: Optional[str]
    password: Optional[str]

class ForgetPasswordRequest(BaseModel):
    email: EmailStr

class ResendVerificationRequest(BaseModel):
    email: EmailStr