"""
Роутер интеграционных заглушек (моков).

- GET  /integration/fx/deals         — симулирует ответ FX-АСУБАНК (список сделок)
- POST /integration/fx/notify        — симулирует получение уведомления о превышении лимита от нас
- GET  /integration/reports/positions — данные позиций для системы ОТЧЕТЫ-АСУБАНК
"""
from datetime import date
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import CurrentUser
from app.services.position_service import calculate_current_position
from app.models.account import Account

router = APIRouter(prefix="/integration", tags=["Интеграция (моки)"])


@router.get("/fx/deals", summary="[МОК FX-АСУБАНК] Список подтверждённых сделок")
def mock_fx_deals(current_user: CurrentUser):
    """
    Заглушка: имитирует данные, которые FX-АСУБАНК мог бы передавать.
    В production эта система была бы внешней.
    """
    return {
        "источник": "FX-АСУБАНК (мок)",
        "сделки": [
            {
                "id": str(uuid4()),
                "тип": "TOD",
                "статус": "Верифицировано",
                "валюта_покупки": "USD",
                "валюта_продажи": "RUB",
                "сумма": 1000000.00,
                "дата_валютирования": str(date.today()),
                "трейдер": "trader01",
            },
            {
                "id": str(uuid4()),
                "тип": "TOM",
                "статус": "Верифицировано",
                "валюта_покупки": "EUR",
                "валюта_продажи": "RUB",
                "сумма": 500000.00,
                "дата_валютирования": str(date.today()),
                "трейдер": "trader02",
            },
        ],
    }


@router.post("/fx/notify", summary="[МОК FX-АСУБАНК] Принять уведомление о превышении лимита")
def mock_fx_receive_notification(body: dict):
    """
    Заглушка: имитирует эндпоинт FX-АСУБАНК, куда мы отправляем уведомление о превышении лимита.
    Логирует полученные данные.
    """
    return {
        "статус": "получено",
        "источник": "ПОЗИЦИИ-АСУБАНК",
        "полученные_данные": body,
    }


@router.get(
    "/reports/positions",
    summary="[МОК ОТЧЕТЫ-АСУБАНК] Позиции по счетам на дату для формирования отчётности",
)
def export_positions_for_reports(
    current_user: CurrentUser,
    дата: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
):
    """
    Эндпоинт, который вызывает система ОТЧЕТЫ-АСУБАНК для получения данных позиций.
    Возвращает позиции по всем активным счетам на указанную дату.
    """
    accounts = db.query(Account).filter(Account.активен == True).all()
    positions = []
    for acc in accounts:
        pos = calculate_current_position(db, acc.id, дата)
        if pos:
            positions.append({
                "счет": pos.номер_счета,
                "наименование": pos.наименование_счета,
                "валюта": pos.код_валюты,
                "дата": str(pos.дата),
                "входящий_остаток": float(pos.входящий_остаток),
                "корректировки": float(pos.сумма_корректировок),
                "оборот_in": float(pos.оборот_in),
                "оборот_out": float(pos.оборот_out),
                "текущая_позиция": float(pos.текущая_позиция),
            })
    return {
        "источник": "ПОЗИЦИИ-АСУБАНК",
        "дата": str(дата),
        "количество_счетов": len(positions),
        "позиции": positions,
    }
