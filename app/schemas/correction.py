from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class CorrectionCreate(BaseModel):
    id_входящего_остатка: UUID
    сумма: Decimal
    комментарий: Optional[str] = None


class CorrectionRead(BaseModel):
    id: UUID
    id_входящего_остатка: UUID
    пользователь_id: UUID
    сумма: Decimal
    комментарий: Optional[str] = None
    дата_время: datetime

    model_config = {"from_attributes": True}
