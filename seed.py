"""
Скрипт заполнения базы данных начальными данными.
Запуск: python seed.py
"""
from datetime import date
from app.database import SessionLocal, Base, engine
from app.models.currency import Currency
from app.models.account import Account
from app.models.user import User, ROLE_ADMIN, ROLE_POSITIONER, ROLE_TRADER
from app.models.opening_balance import OpeningBalance
from app.services.auth_service import hash_password

# Импортируем все модели чтобы создались таблицы
import app.models  # noqa


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # --- Валюты ---
        currencies = [
            Currency(код="USD", наименование="Доллар США", знаков_после_запятой=2),
            Currency(код="EUR", наименование="Евро", знаков_после_запятой=2),
            Currency(код="RUB", наименование="Российский рубль", знаков_после_запятой=2),
            Currency(код="CNY", наименование="Китайский юань", знаков_после_запятой=2),
            Currency(код="GBP", наименование="Британский фунт", знаков_после_запятой=2),
        ]
        for c in currencies:
            if not db.query(Currency).filter(Currency.код == c.код).first():
                db.add(c)
        db.flush()
        print("✓ Валюты добавлены")

        # --- Счета ностро ---
        accounts_data = [
            dict(
                номер_счета="30111840000000001001",
                наименование="Ностро USD в Citibank",
                код_валюты="USD",
                банк_корреспондент="Citibank N.A., New York",
                лимит=500000,
            ),
            dict(
                номер_счета="30111978000000001002",
                наименование="Ностро EUR в Deutsche Bank",
                код_валюты="EUR",
                банк_корреспондент="Deutsche Bank AG, Frankfurt",
                лимит=300000,
            ),
            dict(
                номер_счета="30111156000000001003",
                наименование="Ностро CNY в Bank of China",
                код_валюты="CNY",
                банк_корреспондент="Bank of China, Beijing",
                лимит=2000000,
            ),
            dict(
                номер_счета="30111826000000001004",
                наименование="Ностро GBP в Barclays",
                код_валюты="GBP",
                банк_корреспондент="Barclays Bank PLC, London",
                лимит=200000,
            ),
        ]
        created_accounts = []
        for a in accounts_data:
            existing = db.query(Account).filter(Account.номер_счета == a["номер_счета"]).first()
            if not existing:
                acc = Account(**a)
                db.add(acc)
                db.flush()
                created_accounts.append(acc)
            else:
                created_accounts.append(existing)
        print("✓ Счета ностро добавлены")

        # --- Входящие остатки на сегодня ---
        today = date.today()
        opening_balances = [
            (created_accounts[0], 1_200_000.00),
            (created_accounts[1], 850_000.00),
            (created_accounts[2], 5_000_000.00),
            (created_accounts[3], 400_000.00),
        ]
        for acc, сумма in opening_balances:
            existing = db.query(OpeningBalance).filter(
                OpeningBalance.id_счета == acc.id,
                OpeningBalance.дата == today,
            ).first()
            if not existing:
                db.add(OpeningBalance(id_счета=acc.id, дата=today, сумма=сумма))
        print("✓ Входящие остатки на сегодня добавлены")

        # --- Пользователи ---
        users_data = [
            dict(логин="admin", пароль="Admin@123", полное_имя="Главный Администратор", роль=ROLE_ADMIN),
            dict(логин="positioner01", пароль="Pos@123", полное_имя="Иванов Иван Иванович", роль=ROLE_POSITIONER),
            dict(логин="positioner02", пароль="Pos@123", полное_имя="Петрова Анна Сергеевна", роль=ROLE_POSITIONER),
            dict(логин="trader01", пароль="Trader@123", полное_имя="Сидоров Алексей Петрович", роль=ROLE_TRADER),
            dict(логин="trader02", пароль="Trader@123", полное_имя="Козлова Мария Дмитриевна", роль=ROLE_TRADER),
        ]
        for u in users_data:
            if not db.query(User).filter(User.логин == u["логин"]).first():
                db.add(User(
                    логин=u["логин"],
                    хэш_пароля=hash_password(u["пароль"]),
                    полное_имя=u["полное_имя"],
                    роль=u["роль"],
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
