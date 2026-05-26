from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import CurrentUser, require_positioner_or_admin
from app.models.audit import AuditLog
from app.models.correction import Correction
from app.models.opening_balance import OpeningBalance
from app.schemas.correction import CorrectionCreate, CorrectionRead

router = APIRouter(prefix="/corrections", tags=["Корректировка остатков"])


@router.get(
    "/",
    response_model=list[CorrectionRead],
    summary="История корректировок",
)
def list_corrections(
    current_user: CurrentUser,
    opening_balance_id: UUID | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Correction)
    if opening_balance_id:
        q = q.filter(Correction.opening_balance_id == opening_balance_id)
    return q.order_by(Correction.created_at.desc()).all()


@router.post(
    "/",
    response_model=CorrectionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать корректировку остатка (Позиционер)",
    dependencies=[Depends(require_positioner_or_admin)],
)
def create_correction(
    body: CorrectionCreate,
    current_user: CurrentUser,
    request: Request,
    db: Session = Depends(get_db),
):
    ob = db.query(OpeningBalance).filter(OpeningBalance.id == body.opening_balance_id).first()
    if not ob:
        raise HTTPException(status_code=404, detail="Входящий остаток не найден")

    old_sum = float(ob.corrections_amount)
    ob.corrections_amount += body.amount
    ob.is_corrected = True

    correction = Correction(
        opening_balance_id=ob.id,
        user_id=current_user.id,
        amount=body.amount,
        comment=body.comment,
    )
    db.add(correction)

    db.add(AuditLog(
        user_id=current_user.id,
        login=current_user.login,
        action="CORRECTION_CREATED",
        entity="opening_balances",
        entity_id=str(ob.id),
        details={
            "account_id": str(ob.account_id),
            "date": str(ob.date),
            "correction_amount": float(body.amount),
            "amount_before": old_sum,
            "amount_after": float(ob.corrections_amount),
            "comment": body.comment,
        },
        ip_address=request.client.host if request.client else None,
    ))

    db.commit()
    db.refresh(correction)
    return correction


@router.get(
    "/{correction_id}",
    response_model=CorrectionRead,
    summary="Корректировка по ID",
)
def get_correction(
    correction_id: UUID,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    c = db.query(Correction).filter(Correction.id == correction_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Корректировка не найдена")
    return c
