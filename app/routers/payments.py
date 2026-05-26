from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import CurrentUser
from app.models.account import Account
from app.models.currency import Currency
from app.models.payment import Payment
from app.schemas.payment import IncomingPaymentFromFX, PaymentRead
from app.services.position_service import process_incoming_payment

router = APIRouter(prefix="/payments", tags=["Платежи"])


@router.get("/", response_model=list[PaymentRead], summary="Список платежей")
def list_payments(
    current_user: CurrentUser,
    account_id: UUID | None = None,
    value_date: date | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Payment)
    if account_id:
        q = q.filter(Payment.account_id == account_id)
    if value_date:
        q = q.filter(Payment.value_date == value_date)
    return q.order_by(Payment.processing_date.desc()).all()


@router.get("/{payment_id}", response_model=PaymentRead, summary="Платёж по ID")
def get_payment(payment_id: UUID, current_user: CurrentUser, db: Session = Depends(get_db)):
    p = db.query(Payment).filter(Payment.id == payment_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Платёж не найден")
    return p


@router.post(
    "/incoming",
    status_code=status.HTTP_201_CREATED,
    summary="Принять платёж от FX-АСУБАНК и обновить позицию",
)
def receive_payment_from_fx(body: IncomingPaymentFromFX, db: Session = Depends(get_db)):
    """
    Эндпоинт вызывается системой FX-АСУБАНК при создании/подтверждении сделки.
    Принимает платёж, создаёт запись и пересчитывает позицию.
    """
    if not db.query(Account).filter(Account.id == body.account_id).first():
        raise HTTPException(status_code=400, detail="Счёт не найден")
    if not db.query(Currency).filter(Currency.code == body.currency_code.upper()).first():
        raise HTTPException(status_code=400, detail="Валюта не найдена")
    if body.direction not in ("IN", "OUT"):
        raise HTTPException(status_code=400, detail="Направление должно быть IN или OUT")

    payment = Payment(
        fx_deal_id=body.deal_id,
        currency_code=body.currency_code.upper(),
        amount=body.amount,
        value_date=body.value_date,
        account_id=body.account_id,
        direction=body.direction,
        processing_date=date.today(),
    )
    db.add(payment)
    db.flush()

    result = process_incoming_payment(db, payment)
    db.commit()

    return {
        "status": "accepted",
        "payment_id": str(payment.id),
        **result,
    }
