"""Периодическая синхронизация НСИ из REPORTS-ASUBANK.

Запускается в фоновом потоке раз в NSI_SYNC_INTERVAL_SECONDS секунд.
Также доступна вручную через POST /admin/sync-nsi.

Что синхронизируется:
- Валюты: добавляет новые, обновляет name/is_active у существующих.
- Счета ностро (type=NOSTRO): добавляет новые, обновляет name/bank/is_active.
- Лимиты счетов НЕ трогаются — они хранятся только в POSITIONS.
"""

from __future__ import annotations

import logging
import os
import time
import threading

import httpx
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.account import Account
from app.models.currency import Currency

log = logging.getLogger(__name__)

REPORTS_BASE_URL = os.getenv("REPORTS_BASE_URL", "http://194.67.99.93:8002")
IDP_BASE_URL = os.getenv("IDP_BASE_URL", "http://185.17.3.75:8083")
NSI_SYNC_EMAIL = os.getenv("NSI_SYNC_EMAIL", "positioner01@asubank.local")
NSI_SYNC_PASSWORD = os.getenv("NSI_SYNC_PASSWORD", "Positioner01!")
NSI_SYNC_INTERVAL = int(os.getenv("NSI_SYNC_INTERVAL_SECONDS", "600"))  # 10 минут


def _get_user_token() -> str | None:
    """Логинится в IdP, возвращает access token."""
    try:
        r = httpx.post(
            f"{IDP_BASE_URL.rstrip('/')}/api/v1/auth/login",
            json={"email": NSI_SYNC_EMAIL, "password": NSI_SYNC_PASSWORD},
            timeout=10.0,
        )
        r.raise_for_status()
        data = r.json()
        token = data.get("accessToken") or data.get("access_token")
        return str(token) if token else None
    except Exception as exc:
        log.warning("НСИ-sync: не удалось получить токен IdP (%s): %s", IDP_BASE_URL, exc)
        return None


def sync_nsi(db: Session) -> dict:
    """Синхронизирует НСИ из REPORTS. Возвращает статистику изменений."""
    token = _get_user_token()
    if not token:
        return {
            "ok": False,
            "error": "Не удалось получить токен IdP",
            "currencies_added": 0,
            "currencies_updated": 0,
            "accounts_added": 0,
            "accounts_updated": 0,
        }

    headers = {"Authorization": f"Bearer {token}"}
    base = REPORTS_BASE_URL.rstrip("/")
    result: dict = {
        "ok": True,
        "currencies_added": 0,
        "currencies_updated": 0,
        "accounts_added": 0,
        "accounts_updated": 0,
        "errors": [],
    }

    # --- Валюты ---
    try:
        r = httpx.get(
            f"{base}/api/v1/nsi/currencies",
            headers=headers,
            params={"active_only": "false"},
            timeout=10.0,
        )
        r.raise_for_status()
        for c in r.json():
            code = c["code"].upper()
            name = c.get("name_ru") or c.get("name_en") or code
            decimals = int(c.get("decimal_places", 2))
            is_active = bool(c.get("is_active", True))

            existing = db.query(Currency).filter(Currency.code == code).first()
            if existing is None:
                db.add(Currency(code=code, name=name, decimal_places=decimals))
                result["currencies_added"] += 1
            else:
                changed = False
                if existing.name != name:
                    existing.name = name
                    changed = True
                if existing.decimal_places != decimals:
                    existing.decimal_places = decimals
                    changed = True
                if changed:
                    result["currencies_updated"] += 1
    except Exception as exc:
        msg = f"currencies: {exc}"
        result["errors"].append(msg)
        log.warning("НСИ-sync: %s", msg)

    # --- Счета ностро ---
    try:
        r = httpx.get(
            f"{base}/api/v1/nsi/accounts",
            headers=headers,
            params={"active_only": "false"},
            timeout=10.0,
        )
        r.raise_for_status()
        for a in r.json():
            if a.get("type", "NOSTRO") != "NOSTRO":
                continue
            number = (a.get("account_number") or "").strip()
            if not number:
                continue
            ccy = (a.get("currency_code") or "").upper()
            name = a.get("name", number)
            bank = a.get("bank_name") or ""
            is_active = bool(a.get("is_active", True))

            existing = db.query(Account).filter(Account.account_number == number).first()
            if existing is None:
                if not db.query(Currency).filter(Currency.code == ccy).first():
                    log.debug("НСИ-sync: пропущен счёт %s — валюта %s неизвестна", number, ccy)
                    continue
                db.add(Account(
                    account_number=number,
                    name=name,
                    currency_code=ccy,
                    correspondent_bank=bank,
                    is_active=is_active,
                ))
                result["accounts_added"] += 1
            else:
                changed = False
                if existing.name != name:
                    existing.name = name
                    changed = True
                if existing.correspondent_bank != bank:
                    existing.correspondent_bank = bank
                    changed = True
                if existing.is_active != is_active:
                    existing.is_active = is_active
                    changed = True
                if changed:
                    result["accounts_updated"] += 1
    except Exception as exc:
        msg = f"accounts: {exc}"
        result["errors"].append(msg)
        log.warning("НСИ-sync: %s", msg)

    try:
        db.commit()
        log.info(
            "НСИ-sync: валюты +%d/~%d, счета +%d/~%d",
            result["currencies_added"], result["currencies_updated"],
            result["accounts_added"], result["accounts_updated"],
        )
    except Exception as exc:
        db.rollback()
        result["ok"] = False
        result["errors"].append(f"commit: {exc}")
        log.error("НСИ-sync: ошибка коммита: %s", exc)

    return result


def _sync_loop() -> None:
    """Фоновый поток: синхронизирует НСИ при старте и затем каждые NSI_SYNC_INTERVAL секунд."""
    log.info("НСИ-sync: поток запущен, интервал %d сек", NSI_SYNC_INTERVAL)
    while True:
        db = SessionLocal()
        try:
            sync_nsi(db)
        except Exception as exc:  # noqa: BLE001
            log.warning("НСИ-sync: необработанное исключение: %s", exc)
        finally:
            db.close()
        time.sleep(NSI_SYNC_INTERVAL)


def start_sync_thread() -> threading.Thread:
    t = threading.Thread(target=_sync_loop, name="nsi-sync", daemon=True)
    t.start()
    return t
