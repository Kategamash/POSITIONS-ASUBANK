from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.opening_balance import OpeningBalance
from app.models.payment import Payment, DIRECTION_IN, DIRECTION_OUT
from app.models.position import Position
from app.schemas.position import CurrentPositionRead


def get_or_create_opening_balance(
    db: Session, id_счета: UUID, дата: date
) -> OpeningBalance:
    ob = (
        db.query(OpeningBalance)
        .filter(OpeningBalance.id_счета == id_счета, OpeningBalance.дата == дата)
        .first()
    )
    if not ob:
        ob = OpeningBalance(id_счета=id_счета, дата=дата, сумма=Decimal("0"))
        db.add(ob)
        db.flush()
    return ob


def calculate_current_position(
    db: Session, id_счета: UUID, дата: date
) -> Optional[CurrentPositionRead]:
    account = db.query(Account).filter(Account.id == id_счета).first()
    if not account:
        return None

    ob = (
        db.query(OpeningBalance)
        .filter(OpeningBalance.id_счета == id_счета, OpeningBalance.дата == дата)
        .first()
    )
    opening = ob.сумма if ob else Decimal("0")
    corrections = ob.сумма_корректировок if ob else Decimal("0")

    turnover_in = (
        db.query(func.coalesce(func.sum(Payment.сумма), 0))
        .filter(
            Payment.id_счета == id_счета,
            Payment.дата_валютирования == дата,
            Payment.направление == DIRECTION_IN,
        )
        .scalar()
    )
    turnover_out = (
        db.query(func.coalesce(func.sum(Payment.сумма), 0))
        .filter(
            Payment.id_счета == id_счета,
            Payment.дата_валютирования == дата,
            Payment.направление == DIRECTION_OUT,
        )
        .scalar()
    )

    turnover_in = Decimal(str(turnover_in))
    turnover_out = Decimal(str(turnover_out))
    current = opening + corrections + turnover_in - turnover_out

    limit = account.лимит
    exceeded = limit is not None and current < limit

    return CurrentPositionRead(
        id_счета=account.id,
        номер_счета=account.номер_счета,
        наименование_счета=account.наименование,
        код_валюты=account.код_валюты,
        дата=дата,
        входящий_остаток=opening,
        сумма_корректировок=corrections,
        оборот_in=turnover_in,
        оборот_out=turnover_out,
        текущая_позиция=current,
        лимит=limit,
        превышение_лимита=exceeded,
    )


def process_incoming_payment(db: Session, payment: Payment) -> dict:
    """
    Обрабатывает входящий платёж:
    1. Получает/создаёт входящий остаток для даты валютирования.
    2. Создаёт запись Позиция.
    3. Проверяет лимит — возвращает уведомление если превышен.
    """
    ob = get_or_create_opening_balance(db, payment.id_счета, payment.дата_валютирования)

    position = calculate_current_position(db, payment.id_счета, payment.дата_валютирования)
    current_sum = position.текущая_позиция if position else Decimal("0")

    pos = Position(
        id_платежа=payment.id,
        id_входящего_остатка=ob.id,
        дата=payment.дата_валютирования,
        сумма=current_sum,
    )
    db.add(pos)
    db.flush()

    limit_exceeded = position.превышение_лимита if position else False
    return {
        "позиция_id": str(pos.id),
        "текущая_позиция": float(current_sum),
        "превышение_лимита": limit_exceeded,
    }
