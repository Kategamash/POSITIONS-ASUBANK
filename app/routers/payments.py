from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import CurrentUser, ServicePrincipal, require_service_scope
from app.models.account import Account
from app.models.audit import AuditLog
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
def receive_payment_from_fx(
    body: IncomingPaymentFromFX,
    request: Request,
    service: ServicePrincipal = Depends(require_service_scope("fx-dealing:write")),
    db: Session = Depends(get_db),
):
    """
    Эндпоинт вызывается системой FX-АСУБАНК при подтверждении сделки позиционером.
    Принимает платёж, создаёт запись и пересчитывает позицию.
    Можно указать счёт либо account_id (UUID), либо account_number.
    """
    _ = service
    account = None
    if body.account_id:
        account = db.query(Account).filter(Account.id == body.account_id).first()
    elif body.account_number:
        account = (
            db.query(Account)
            .filter(
                (Account.account_number == body.account_number)
                | (Account.name == body.account_number)
            )
            .first()
        )

    if not account:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Счёт не найден: account_id={body.account_id}, account_number={body.account_number}"
            ),
        )
    if not db.query(Currency).filter(Currency.code == body.currency_code.upper()).first():
        raise HTTPException(status_code=400, detail=f"Валюта не найдена: {body.currency_code}")
    if body.direction not in ("IN", "OUT"):
        raise HTTPException(status_code=400, detail="Направление должно быть IN или OUT")

    payment = Payment(
        fx_deal_id=body.deal_id,
        currency_code=body.currency_code.upper(),
        amount=body.amount,
        value_date=body.value_date,
        account_id=account.id,
        direction=body.direction,
        processing_date=date.today(),
    )
    db.add(payment)
    db.flush()

    result = process_incoming_payment(db, payment)
    db.add(AuditLog(
        login=service.client_id,
        action="FX_PAYMENT_RECEIVED",
        entity="payments",
        entity_id=str(payment.id),
        details={
            "service": service.service,
            "scopes": list(service.scopes),
            "deal_id": str(body.deal_id),
            "account_number": account.account_number,
            "currency_code": body.currency_code.upper(),
            "amount": float(body.amount),
            "direction": body.direction,
            "value_date": str(body.value_date),
            "correlation_id": body.correlation_id,
            **result,
        },
        ip_address=request.client.host if request.client else None,
    ))
    db.commit()

    return {
        "status": "accepted",
        "payment_id": str(payment.id),
        "account_id": str(account.id),
        "account_number": account.account_number,
        "correlation_id": body.correlation_id,
        **result,
    }
