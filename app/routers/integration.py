"""
Integration mock router.

- GET  /integration/fx/deals          — mock FX-ASUBANK deals list
- POST /integration/fx/notify         — mock limit exceeded notification receiver
- GET  /integration/reports/positions — position export for REPORTS-ASUBANK
"""
from datetime import date
from uuid import uuid4

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import CurrentUser
from app.services.position_service import calculate_current_position
from app.models.account import Account

router = APIRouter(prefix="/integration", tags=["Интеграция (моки)"])


@router.get("/fx/deals", summary="[МОК FX-АСУБАНК] Список подтверждённых сделок")
def mock_fx_deals(current_user: CurrentUser):
    return {
        "source": "FX-ASUBANK (mock)",
        "deals": [
            {
                "id": str(uuid4()),
                "type": "TOD",
                "status": "Verified",
                "buy_currency": "USD",
                "sell_currency": "RUB",
                "amount": 1000000.00,
                "value_date": str(date.today()),
                "trader": "trader01",
            },
            {
                "id": str(uuid4()),
                "type": "TOM",
                "status": "Verified",
                "buy_currency": "EUR",
                "sell_currency": "RUB",
                "amount": 500000.00,
                "value_date": str(date.today()),
                "trader": "trader02",
            },
        ],
    }


@router.post("/fx/notify", summary="[МОК FX-АСУБАНК] Принять уведомление о превышении лимита")
def mock_fx_receive_notification(body: dict):
    return {
        "status": "received",
        "source": "POSITIONS-ASUBANK",
        "received_data": body,
    }


@router.get(
    "/reports/positions",
    summary="[МОК ОТЧЕТЫ-АСУБАНК] Позиции по счетам на дату для формирования отчётности",
)
def export_positions_for_reports(
    current_user: CurrentUser,
    date: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
):
    accounts = db.query(Account).filter(Account.is_active == True).all()
    positions = []
    for acc in accounts:
        pos = calculate_current_position(db, acc.id, date)
        if pos:
            positions.append({
                "account_number": pos.account_number,
                "name": pos.account_name,
                "currency_code": pos.currency_code,
                "date": str(pos.date),
                "opening_balance": float(pos.opening_balance),
                "corrections_amount": float(pos.corrections_amount),
                "turnover_in": float(pos.turnover_in),
                "turnover_out": float(pos.turnover_out),
                "current_position": float(pos.current_position),
            })
    return {
        "source": "POSITIONS-ASUBANK",
        "date": str(date),
        "account_count": len(positions),
        "positions": positions,
    }
