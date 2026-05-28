"""Идемпотентный авто-seed справочников (валюты, ностро-счета, входящие остатки).

Пользователей не сидим: управление пользователями переехало в Identity Provider.
"""

from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.account import Account
from app.models.currency import Currency
from app.models.opening_balance import OpeningBalance


_DEFAULT_CURRENCIES = [
    ("USD", "Доллар США", 2),
    ("EUR", "Евро", 2),
    ("RUB", "Российский рубль", 2),
    ("CNY", "Китайский юань", 2),
    ("GBP", "Фунт стерлингов", 2),
    ("CHF", "Швейцарский франк", 2),
    ("JPY", "Японская иена", 0),
    ("KZT", "Казахстанский тенге", 2),
    ("TRY", "Турецкая лира", 2),
    ("AUD", "Австралийский доллар", 2),
]

# Номера счетов синхронизированы с НСИ REPORTS-ASUBANK (reports-asubank/app/core/seed.py).
# Лимиты — оперативные данные POSITIONS, в REPORTS не хранятся.
_DEFAULT_ACCOUNTS = [
    dict(
        account_number="30101810400000000225",
        name="Корреспондентский счёт RUB",
        currency_code="RUB",
        correspondent_bank="Банк России",
        limit=150_000_000,
    ),
    dict(
        account_number="30101810200000000999",
        name="Nostro USD New York",
        currency_code="USD",
        correspondent_bank="Global Clearing Bank NY",
        limit=2_000_000,
    ),
    dict(
        account_number="30101810900000000888",
        name="Nostro EUR Frankfurt",
        currency_code="EUR",
        correspondent_bank="Euro Settlement Bank",
        limit=1_500_000,
    ),
    dict(
        account_number="30101810600000000777",
        name="Nostro GBP London",
        currency_code="GBP",
        correspondent_bank="Global Markets Bank London",
        limit=5_000_000,
    ),
    dict(
        account_number="30101810800000000666",
        name="Nostro CNY Shanghai",
        currency_code="CNY",
        correspondent_bank="Shanghai Treasury Bank",
        limit=8_000_000,
    ),
    dict(
        account_number="30101810700000000555",
        name="Nostro CHF Zurich",
        currency_code="CHF",
        correspondent_bank="Helvetia Private Bank",
        limit=3_000_000,
    ),
]


def _ensure_currencies(db: Session) -> None:
    for code, name, decimals in _DEFAULT_CURRENCIES:
        if not db.query(Currency).filter(Currency.code == code).first():
            db.add(Currency(code=code, name=name, decimal_places=decimals))


def _ensure_accounts(db: Session) -> list[Account]:
    accounts: list[Account] = []
    for spec in _DEFAULT_ACCOUNTS:
        existing = (
            db.query(Account)
            .filter(Account.account_number == spec["account_number"])
            .first()
        )
        if existing:
            existing.limit = spec["limit"]
            accounts.append(existing)
            continue
        acc = Account(**spec)
        db.add(acc)
        db.flush()
        accounts.append(acc)
    return accounts


def _ensure_opening_balances(db: Session, accounts: list[Account]) -> None:
    today = date.today()
    # Порядок соответствует _DEFAULT_ACCOUNTS: RUB, USD, EUR, GBP, CNY, CHF
    initial = [100_000_000, 1_200_000, 850_000, 500_000, 5_000_000, 1_000_000]
    for acc, amount in zip(accounts, initial):
        for day_offset in range(30):
            target_date = today - timedelta(days=day_offset)
            existing = (
                db.query(OpeningBalance)
                .filter(OpeningBalance.account_id == acc.id, OpeningBalance.date == target_date)
                .first()
            )
            if not existing:
                db.add(OpeningBalance(account_id=acc.id, date=target_date, amount=amount))


def seed_default_data() -> None:
    db = SessionLocal()
    try:
        _ensure_currencies(db)
        accounts = _ensure_accounts(db)
        _ensure_opening_balances(db, accounts)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
