from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SignupRequest(BaseModel):
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", min_length=5, max_length=255)
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    email: str


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool
    is_admin: bool
    created_at: datetime

