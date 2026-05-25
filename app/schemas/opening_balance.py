from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class OpeningBalanceBase(BaseModel):
    id_счета: UUID
    дата: date
    сумма: Decimal = Decimal("0")


class OpeningBalanceCreate(OpeningBalanceBase):
    pass


class OpeningBalanceRead(OpeningBalanceBase):
    id: UUID
    сумма_корректировок: Decimal
    скорректирован: bool
    дата_расчета: Optional[datetime] = None

    model_config = {"from_attributes": True}
