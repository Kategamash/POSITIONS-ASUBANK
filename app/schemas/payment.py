from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class PaymentBase(BaseModel):
    currency_code: str
    amount: Decimal
    value_date: date
    account_id: UUID
    direction: str  # IN / OUT
    processing_date: date


class PaymentCreate(PaymentBase):
    fx_deal_id: Optional[UUID] = None


class PaymentRead(PaymentBase):
    id: UUID
    fx_deal_id: Optional[UUID] = None

    model_config = {"from_attributes": True}


class IncomingPaymentFromFX(BaseModel):
    """Incoming payment from FX-DEAL-MANAGER.

    Можно указывать счёт либо UUID (account_id), либо номером (account_number).
    """

    deal_id: UUID
    currency_code: str
    amount: Decimal
    value_date: date
    direction: str  # IN / OUT
    account_id: Optional[UUID] = None
    account_number: Optional[str] = None
    correlation_id: Optional[str] = None
