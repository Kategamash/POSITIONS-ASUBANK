from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class PaymentBase(BaseModel):
    код_валюты: str
    сумма: Decimal
    дата_валютирования: date
    id_счета: UUID
    направление: str  # IN / OUT
    дата_обработки: date


class PaymentCreate(PaymentBase):
    id_сделки_fx: Optional[UUID] = None


class PaymentRead(PaymentBase):
    id: UUID
    id_сделки_fx: Optional[UUID] = None

    model_config = {"from_attributes": True}


class IncomingPaymentFromFX(BaseModel):
    """Схема входящего платежа от FX-АСУБАНК"""
    id_сделки: UUID
    код_валюты: str
    сумма: Decimal
    дата_валютирования: date
    id_счета: UUID
    направление: str  # IN / OUT
