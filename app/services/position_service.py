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
    db: Session, account_id: UUID, date: date
) -> OpeningBalance:
    ob = (
        db.query(OpeningBalance)
        .filter(OpeningBalance.account_id == account_id, OpeningBalance.date == date)
        .first()
    )
    if not ob:
        ob = OpeningBalance(account_id=account_id, date=date, amount=Decimal("0"))
        db.add(ob)
        db.flush()
    return ob


def calculate_current_position(
    db: Session, account_id: UUID, date: date
) -> Optional[CurrentPositionRead]:
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        return None

    ob = (
        db.query(OpeningBalance)
        .filter(OpeningBalance.account_id == account_id, OpeningBalance.date == date)
        .first()
    )
    opening = ob.amount if ob else Decimal("0")
    corrections = ob.corrections_amount if ob else Decimal("0")

    turnover_in = (
        db.query(func.coalesce(func.sum(Payment.amount), 0))
        .filter(
            Payment.account_id == account_id,
            Payment.value_date == date,
            Payment.direction == DIRECTION_IN,
        )
        .scalar()
    )
    turnover_out = (
        db.query(func.coalesce(func.sum(Payment.amount), 0))
        .filter(
            Payment.account_id == account_id,
            Payment.value_date == date,
            Payment.direction == DIRECTION_OUT,
        )
        .scalar()
    )

    turnover_in = Decimal(str(turnover_in))
    turnover_out = Decimal(str(turnover_out))
    current = opening + corrections + turnover_in - turnover_out

    limit = account.limit
    exceeded = limit is not None and current < limit

    return CurrentPositionRead(
        account_id=account.id,
        account_number=account.account_number,
        account_name=account.name,
        currency_code=account.currency_code,
        date=date,
        opening_balance=opening,
        corrections_amount=corrections,
        turnover_in=turnover_in,
        turnover_out=turnover_out,
        current_position=current,
        limit=limit,
        limit_exceeded=exceeded,
    )


def process_incoming_payment(db: Session, payment: Payment) -> dict:
    """
    Process incoming payment:
    1. Get/create opening balance for value date.
    2. Create position record.
    3. Check limit — return notification if exceeded.
    """
    ob = get_or_create_opening_balance(db, payment.account_id, payment.value_date)

    position = calculate_current_position(db, payment.account_id, payment.value_date)
    current_sum = position.current_position if position else Decimal("0")

    pos = Position(
        payment_id=payment.id,
        opening_balance_id=ob.id,
        date=payment.value_date,
        amount=current_sum,
    )
    db.add(pos)
    db.flush()

    limit_exceeded = position.limit_exceeded if position else False
    return {
        "position_id": str(pos.id),
        "current_position": float(current_sum),
        "limit_exceeded": limit_exceeded,
    }
