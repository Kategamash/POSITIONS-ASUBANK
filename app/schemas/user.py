from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class UserCreate(BaseModel):
    логин: str
    пароль: str
    полное_имя: str
    роль: str  # TRADER / POSITIONER / ADMIN


class UserUpdate(BaseModel):
    полное_имя: Optional[str] = None
    роль: Optional[str] = None
    активен: Optional[bool] = None
    пароль: Optional[str] = None


class UserRead(BaseModel):
    id: UUID
    логин: str
    полное_имя: str
    роль: str
    активен: bool
    дата_создания: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    пользователь: UserRead


class LoginRequest(BaseModel):
    логин: str
    пароль: str
