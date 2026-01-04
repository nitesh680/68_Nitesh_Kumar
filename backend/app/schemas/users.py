from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    mobile: Optional[str] = None
    date_of_birth: Optional[date] = None


class UserProfileResponse(BaseModel):
    id: str
    email: EmailStr
    name: str
    mobile: Optional[str] = None
    date_of_birth: Optional[date] = None
    avatar_url: Optional[str] = None
    created_at: Optional[str] = None


class AvatarUploadResponse(BaseModel):
    avatar_url: str
