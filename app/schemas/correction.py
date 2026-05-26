from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class CorrectionCreate(BaseModel):
    opening_balance_id: UUID
    amount: Decimal
    comment: Optional[str] = None


class CorrectionRead(BaseModel):
    id: UUID
    opening_balance_id: UUID
    user_id: UUID
    amount: Decimal
    comment: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
