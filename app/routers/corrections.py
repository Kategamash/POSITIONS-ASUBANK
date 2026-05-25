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
    id_входящего_остатка: UUID | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Correction)
    if id_входящего_остатка:
        q = q.filter(Correction.id_входящего_остатка == id_входящего_остатка)
    return q.order_by(Correction.дата_время.desc()).all()


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
    ob = db.query(OpeningBalance).filter(OpeningBalance.id == body.id_входящего_остатка).first()
    if not ob:
        raise HTTPException(status_code=404, detail="Входящий остаток не найден")

    old_sum = float(ob.сумма_корректировок)
    ob.сумма_корректировок += body.сумма
    ob.скорректирован = True

    correction = Correction(
        id_входящего_остатка=ob.id,
        пользователь_id=current_user.id,
        сумма=body.сумма,
        комментарий=body.комментарий,
    )
    db.add(correction)

    db.add(AuditLog(
        пользователь_id=current_user.id,
        логин=current_user.логин,
        действие="CORRECTION_CREATED",
        сущность="входящий_остаток",
        сущность_id=str(ob.id),
        детали={
            "счет_id": str(ob.id_счета),
            "дата": str(ob.дата),
            "сумма_корректировки": float(body.сумма),
            "сумма_до": old_sum,
            "сумма_после": float(ob.сумма_корректировок),
            "комментарий": body.комментарий,
        },
        ip_адрес=request.client.host if request.client else None,
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
