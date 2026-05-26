from datetime import date
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel


class PositionRead(BaseModel):
    id: UUID
    payment_id: UUID
    opening_balance_id: UUID
    date: date
    amount: Decimal

    model_config = {"from_attributes": True}


class CurrentPositionRead(BaseModel):
    """Current position for an account — aggregated calculation"""
    account_id: UUID
    account_number: str
    account_name: str
    currency_code: str
    date: date
    opening_balance: Decimal
    corrections_amount: Decimal
    turnover_in: Decimal
    turnover_out: Decimal
    current_position: Decimal
    limit: Decimal | None
    limit_exceeded: bool
