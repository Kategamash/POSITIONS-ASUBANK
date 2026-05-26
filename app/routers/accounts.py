from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import CurrentUser, require_admin
from app.models.account import Account
from app.models.currency import Currency
from app.schemas.account import AccountCreate, AccountRead, AccountUpdate

router = APIRouter(prefix="/accounts", tags=["Счета ностро"])


@router.get("/", response_model=list[AccountRead], summary="Список счетов ностро")
def list_accounts(
    current_user: CurrentUser,
    is_active: bool | None = None,
    currency_code: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(Account)
    if is_active is not None:
        q = q.filter(Account.is_active == is_active)
    if currency_code:
        q = q.filter(Account.currency_code == currency_code.upper())
    return q.all()


@router.get("/{account_id}", response_model=AccountRead, summary="Счёт по ID")
def get_account(account_id: UUID, current_user: CurrentUser, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Счёт не найден")
    return account


@router.post(
    "/",
    response_model=AccountRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать счёт ностро (Администратор)",
    dependencies=[Depends(require_admin)],
)
def create_account(body: AccountCreate, db: Session = Depends(get_db)):
    if not db.query(Currency).filter(Currency.code == body.currency_code.upper()).first():
        raise HTTPException(status_code=400, detail="Валюта не найдена")
    if db.query(Account).filter(Account.account_number == body.account_number).first():
        raise HTTPException(status_code=409, detail="Счёт с таким номером уже существует")
    account = Account(**body.model_dump())
    account.currency_code = body.currency_code.upper()
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.patch(
    "/{account_id}",
    response_model=AccountRead,
    summary="Изменить счёт (Администратор)",
    dependencies=[Depends(require_admin)],
)
def update_account(account_id: UUID, body: AccountUpdate, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Счёт не найден")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(account, field, value)
    db.commit()
    db.refresh(account)
    return account
