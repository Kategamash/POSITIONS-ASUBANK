"""Интеграционные эндпоинты ПОЗИЦИИ-АСУБАНК.

* GET /integration/reports/positions — выгрузка позиций по счетам на дату.
  Используется ОТЧЁТЫ-АСУБАНК для построения отчётности.
* GET /integration/fx/deals — proxy к реальному FX-DEAL-MANAGER.
"""

import os
from datetime import date as date_type

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import CurrentUser, require_user_or_service_scope
from app.models.account import Account
from app.services.position_service import calculate_current_position

router = APIRouter(prefix="/integration", tags=["Интеграция"])

FX_BASE_URL = os.getenv("FX_BASE_URL", "http://185.17.3.75:8000")


def _bearer_from_request(request: Request) -> str:
    auth = request.headers.get("authorization")
    if auth:
        return auth
    token = request.cookies.get("access_token")
    if token:
        return f"Bearer {token}"
    raise HTTPException(status_code=401, detail="Отсутствует токен доступа")


@router.get("/fx/health", summary="Проверка доступности FX-DEAL-MANAGER")
async def fx_health():
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.get(f"{FX_BASE_URL.rstrip('/')}/api/v1/health")
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"FX недоступен: {exc}") from exc
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text or "FX health check failed")
    return r.json()


@router.get("/fx/deals", summary="Реальные FX-сделки из FX-DEAL-MANAGER")
async def list_fx_deals(
    request: Request,
    current_user: CurrentUser,
    status: str | None = Query(default="APPROVED"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
):
    _ = current_user
    params: dict[str, object] = {"page": page, "page_size": page_size}
    if status:
        params["status"] = status

    headers = {"Authorization": _bearer_from_request(request)}
    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            r = await client.get(
                f"{FX_BASE_URL.rstrip('/')}/api/v1/deals",
                params=params,
                headers=headers,
            )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"FX недоступен: {exc}") from exc

    if r.status_code >= 400:
        try:
            detail = r.json()
        except Exception:  # noqa: BLE001
            detail = r.text or "Ошибка FX"
        raise HTTPException(status_code=r.status_code, detail=detail)

    payload = r.json()
    items = payload.get("items", payload if isinstance(payload, list) else [])
    deals = [
        {
            "id": item.get("id"),
            "type": item.get("deal_type"),
            "status": item.get("status"),
            "validation_status": item.get("validation_status"),
            "buy_currency": item.get("buy_currency"),
            "sell_currency": item.get("sell_currency"),
            "amount": item.get("amount"),
            "rate": item.get("rate"),
            "value_date": item.get("value_date"),
            "trader": item.get("trader_email") or item.get("trader_id"),
            "payments": item.get("payments", []),
        }
        for item in items
    ]

    return {
        "source": "FX-DEAL-MANAGER",
        "status": status,
        "page": payload.get("page", page) if isinstance(payload, dict) else page,
        "page_size": payload.get("page_size", page_size) if isinstance(payload, dict) else page_size,
        "total": payload.get("total", len(deals)) if isinstance(payload, dict) else len(deals),
        "deals": deals,
    }


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
