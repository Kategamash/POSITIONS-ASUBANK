from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class AccountBase(BaseModel):
    account_number: str
    name: str
    currency_code: str
    correspondent_bank: str
    limit: Optional[Decimal] = None
    is_active: bool = True


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    correspondent_bank: Optional[str] = None
    limit: Optional[Decimal] = None
    is_active: Optional[bool] = None


class AccountRead(AccountBase):
    id: UUID

    model_config = {"from_attributes": True}
