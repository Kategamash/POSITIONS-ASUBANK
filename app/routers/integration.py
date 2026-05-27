"""Интеграционные эндпоинты ПОЗИЦИИ-АСУБАНК.

* GET /integration/reports/positions — выгрузка позиций по счетам на дату.
  Используется ОТЧЁТЫ-АСУБАНК для построения отчётности.

Моковые эндпоинты для FX удалены: получение реальных платежей идёт через
POST /payments/incoming, который дёргает FX-DEAL-MANAGER при подтверждении
сделки.
"""

from datetime import date as date_type

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_user_or_service_scope
from app.models.account import Account
from app.services.position_service import calculate_current_position

router = APIRouter(prefix="/integration", tags=["Интеграция"])


@router.get(
    "/reports/positions",
    summary="Позиции по счетам на дату для ОТЧЁТЫ-АСУБАНК",
)
def export_positions_for_reports(
    _actor=Depends(require_user_or_service_scope("reports:read", "positioner:read", "fx-dealing:read")),
    date: date_type = Query(default_factory=date_type.today),
    currency_code: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    q = db.query(Account).filter(Account.is_active == True)  # noqa: E712
    if currency_code:
        q = q.filter(Account.currency_code == currency_code.upper())

    positions = []
    for acc in q.all():
        pos = calculate_current_position(db, acc.id, date)
        if pos is None:
            continue
        positions.append(
            {
                "account_number": pos.account_number,
                "name": pos.account_name,
                "currency_code": pos.currency_code,
                "date": str(pos.date),
                "opening_balance": float(pos.opening_balance),
                "corrections_amount": float(pos.corrections_amount),
                "turnover_in": float(pos.turnover_in),
                "turnover_out": float(pos.turnover_out),
                "current_position": float(pos.current_position),
            }
        )
    return {
        "source": "POSITIONS-ASUBANK",
        "date": str(date),
        "account_count": len(positions),
        "positions": positions,
    }
