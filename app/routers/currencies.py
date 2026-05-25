from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import CurrentUser, require_admin
from app.models.currency import Currency
from app.schemas.currency import CurrencyCreate, CurrencyRead

router = APIRouter(prefix="/currencies", tags=["Валюты (НСИ)"])


@router.get("/", response_model=list[CurrencyRead], summary="Список валют")
def list_currencies(current_user: CurrentUser, db: Session = Depends(get_db)):
    return db.query(Currency).all()


@router.get("/{код}", response_model=CurrencyRead, summary="Валюта по коду")
def get_currency(код: str, current_user: CurrentUser, db: Session = Depends(get_db)):
    currency = db.query(Currency).filter(Currency.код == код.upper()).first()
    if not currency:
        raise HTTPException(status_code=404, detail="Валюта не найдена")
    return currency


@router.post(
    "/",
    response_model=CurrencyRead,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить валюту (Администратор)",
    dependencies=[Depends(require_admin)],
)
def create_currency(body: CurrencyCreate, db: Session = Depends(get_db)):
    if db.query(Currency).filter(Currency.код == body.код.upper()).first():
        raise HTTPException(status_code=409, detail="Валюта с таким кодом уже существует")
    currency = Currency(
        код=body.код.upper(),
        наименование=body.наименование,
        знаков_после_запятой=body.знаков_после_запятой,
    )
    db.add(currency)
    db.commit()
    db.refresh(currency)
    return currency


@router.delete(
    "/{код}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить валюту (Администратор)",
    dependencies=[Depends(require_admin)],
)
def delete_currency(код: str, db: Session = Depends(get_db)):
    currency = db.query(Currency).filter(Currency.код == код.upper()).first()
    if not currency:
        raise HTTPException(status_code=404, detail="Валюта не найдена")
    db.delete(currency)
    db.commit()
