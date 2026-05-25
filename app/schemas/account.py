from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class AccountBase(BaseModel):
    номер_счета: str
    наименование: str
    код_валюты: str
    банк_корреспондент: str
    лимит: Optional[Decimal] = None
    активен: bool = True


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    наименование: Optional[str] = None
    банк_корреспондент: Optional[str] = None
    лимит: Optional[Decimal] = None
    активен: Optional[bool] = None


class AccountRead(AccountBase):
    id: UUID

    model_config = {"from_attributes": True}
