from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import CurrentUser
from app.models.account import Account
from app.models.opening_balance import OpeningBalance
from app.schemas.opening_balance import OpeningBalanceCreate, OpeningBalanceRead
from app.schemas.position import CurrentPositionRead
from app.services.position_service import calculate_current_position

router = APIRouter(prefix="/positions", tags=["Мониторинг позиций"])


@router.get(
    "/",
    response_model=list[CurrentPositionRead],
    summary="Текущие позиции по всем счетам",
)
def get_all_positions(
    current_user: CurrentUser,
    дата: date = Query(default_factory=date.today),
    код_валюты: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Account).filter(Account.активен == True)
    if код_валюты:
        query = query.filter(Account.код_валюты == код_валюты.upper())

    result = []
    for account in query.all():
        pos = calculate_current_position(db, account.id, дата)
        if pos:
            result.append(pos)
    return result


@router.get(
    "/{account_id}",
    response_model=CurrentPositionRead,
    summary="Позиция по конкретному счёту",
)
def get_position(
    account_id: UUID,
    current_user: CurrentUser,
    дата: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Счёт не найден")
    pos = calculate_current_position(db, account_id, дата)
    if not pos:
        raise HTTPException(status_code=404, detail="Позиция не найдена")
    return pos


@router.get(
    "/opening-balances/",
    response_model=list[OpeningBalanceRead],
    summary="Входящие остатки",
)
def list_opening_balances(
    current_user: CurrentUser,
    дата: date | None = None,
    id_счета: UUID | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(OpeningBalance)
    if дата:
        q = q.filter(OpeningBalance.дата == дата)
    if id_счета:
        q = q.filter(OpeningBalance.id_счета == id_счета)
    return q.order_by(OpeningBalance.дата.desc()).all()


@router.post(
    "/opening-balances/",
    response_model=OpeningBalanceRead,
    status_code=201,
    summary="Установить входящий остаток на дату",
)
def create_opening_balance(
    body: OpeningBalanceCreate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    from app.dependencies import require_positioner_or_admin
    require_positioner_or_admin(current_user)

    if not db.query(Account).filter(Account.id == body.id_счета).first():
        raise HTTPException(status_code=400, detail="Счёт не найден")

    existing = (
        db.query(OpeningBalance)
        .filter(
            OpeningBalance.id_счета == body.id_счета,
            OpeningBalance.дата == body.дата,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Входящий остаток на эту дату уже существует. Используйте корректировку.",
        )

    ob = OpeningBalance(id_счета=body.id_счета, дата=body.дата, сумма=body.сумма)
    db.add(ob)
    db.commit()
    db.refresh(ob)
    return ob
