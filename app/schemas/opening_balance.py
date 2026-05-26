from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class OpeningBalanceBase(BaseModel):
    account_id: UUID
    date: date
    amount: Decimal = Decimal("0")


class OpeningBalanceCreate(OpeningBalanceBase):
    pass


class OpeningBalanceRead(OpeningBalanceBase):
    id: UUID
    corrections_amount: Decimal
    is_corrected: bool
    calculated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
