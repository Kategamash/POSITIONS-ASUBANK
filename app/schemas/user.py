from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class UserCreate(BaseModel):
    login: str
    password: str
    full_name: str
    role: str  # TRADER / POSITIONER / ADMIN


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserRead(BaseModel):
    id: UUID
    login: str
    full_name: str
    role: str
    is_active: bool
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class LoginRequest(BaseModel):
    login: str
    password: str
