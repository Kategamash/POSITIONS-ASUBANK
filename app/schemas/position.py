from datetime import date
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel


class PositionRead(BaseModel):
    id: UUID
    id_платежа: UUID
    id_входящего_остатка: UUID
    дата: date
    сумма: Decimal

    model_config = {"from_attributes": True}


class CurrentPositionRead(BaseModel):
    """Текущая позиция по счёту — агрегированный расчёт"""
    id_счета: UUID
    номер_счета: str
    наименование_счета: str
    код_валюты: str
    дата: date
    входящий_остаток: Decimal
    сумма_корректировок: Decimal
    оборот_in: Decimal
    оборот_out: Decimal
    текущая_позиция: Decimal
    лимит: Decimal | None
    превышение_лимита: bool
