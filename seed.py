"""
Seed script for initial database data.
Run: python seed.py
"""
from datetime import date
from app.database import SessionLocal, Base, engine
from app.models.currency import Currency
from app.models.account import Account
from app.models.user import User, ROLE_ADMIN, ROLE_POSITIONER, ROLE_TRADER
from app.models.opening_balance import OpeningBalance
from app.services.auth_service import hash_password

import app.models  # noqa


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        currencies = [
            Currency(code="USD", name="Доллар США", decimal_places=2),
            Currency(code="EUR", name="Евро", decimal_places=2),
            Currency(code="RUB", name="Российский рубль", decimal_places=2),
            Currency(code="CNY", name="Китайский юань", decimal_places=2),
            Currency(code="GBP", name="Британский фунт", decimal_places=2),
        ]
        for c in currencies:
            if not db.query(Currency).filter(Currency.code == c.code).first():
                db.add(c)
        db.flush()
        print("✓ Валюты добавлены")

        accounts_data = [
            dict(
                account_number="30111840000000001001",
                name="Ностро USD в Citibank",
                currency_code="USD",
                correspondent_bank="Citibank N.A., New York",
                limit=500000,
            ),
            dict(
                account_number="30111978000000001002",
                name="Ностро EUR в Deutsche Bank",
                currency_code="EUR",
                correspondent_bank="Deutsche Bank AG, Frankfurt",
                limit=300000,
            ),
            dict(
                account_number="30111156000000001003",
                name="Ностро CNY в Bank of China",
                currency_code="CNY",
                correspondent_bank="Bank of China, Beijing",
                limit=2000000,
            ),
            dict(
                account_number="30111826000000001004",
                name="Ностро GBP в Barclays",
                currency_code="GBP",
                correspondent_bank="Barclays Bank PLC, London",
                limit=200000,
            ),
        ]
        created_accounts = []
        for a in accounts_data:
            existing = db.query(Account).filter(Account.account_number == a["account_number"]).first()
            if not existing:
                acc = Account(**a)
                db.add(acc)
                db.flush()
                created_accounts.append(acc)
            else:
                created_accounts.append(existing)
        print("✓ Счета ностро добавлены")

        today = date.today()
        opening_balances = [
            (created_accounts[0], 1_200_000.00),
            (created_accounts[1], 850_000.00),
            (created_accounts[2], 5_000_000.00),
            (created_accounts[3], 400_000.00),
        ]
        for acc, amount in opening_balances:
            existing = db.query(OpeningBalance).filter(
                OpeningBalance.account_id == acc.id,
                OpeningBalance.date == today,
            ).first()
            if not existing:
                db.add(OpeningBalance(account_id=acc.id, date=today, amount=amount))
        print("✓ Входящие остатки на сегодня добавлены")

        users_data = [
            dict(login="admin", password="Admin@123", full_name="Главный Администратор", role=ROLE_ADMIN),
            dict(login="positioner01", password="Pos@123", full_name="Иванов Иван Иванович", role=ROLE_POSITIONER),
            dict(login="positioner02", password="Pos@123", full_name="Петрова Анна Сергеевна", role=ROLE_POSITIONER),
            dict(login="trader01", password="Trader@123", full_name="Сидоров Алексей Петрович", role=ROLE_TRADER),
            dict(login="trader02", password="Trader@123", full_name="Козлова Мария Дмитриевна", role=ROLE_TRADER),
        ]
        for u in users_data:
            if not db.query(User).filter(User.login == u["login"]).first():
                db.add(User(
                    login=u["login"],
                    password_hash=hash_password(u["password"]),
                    full_name=u["full_name"],
                    role=u["role"],
                ))
        print("✓ Пользователи добавлены")

        db.commit()
        print("\n=== Готово! Начальные данные загружены. ===")
        print("\nУчётные данные для входа:")
        print("  Администратор: admin / Admin@123")
        print("  Позиционер:    positioner01 / Pos@123")
        print("  Трейдер:       trader01 / Trader@123")

    except Exception as e:
        db.rollback()
        print(f"Ошибка: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
