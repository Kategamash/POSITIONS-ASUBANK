"""Initial schema and bootstrap data.

Revision ID: 20260527_0001
Revises:
Create Date: 2026-05-27 01:35:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260527_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ADMIN_ID = "11111111-1111-1111-1111-111111111111"
POSITIONER_01_ID = "22222222-2222-2222-2222-222222222222"
POSITIONER_02_ID = "33333333-3333-3333-3333-333333333333"
TRADER_01_ID = "44444444-4444-4444-4444-444444444444"
TRADER_02_ID = "55555555-5555-5555-5555-555555555555"

USD_ACCOUNT_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1"
EUR_ACCOUNT_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2"
CNY_ACCOUNT_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3"
GBP_ACCOUNT_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa4"


def upgrade() -> None:
    op.create_table(
        "currencies",
        sa.Column("code", sa.String(length=3), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("decimal_places", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint("code"),
    )

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("login", sa.String(length=50), nullable=False),
        sa.Column("password_hash", sa.String(length=200), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("login"),
    )

    op.create_table(
        "accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_number", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("currency_code", sa.String(length=3), nullable=False),
        sa.Column("correspondent_bank", sa.String(length=200), nullable=False),
        sa.Column("limit", sa.Numeric(20, 2), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["currency_code"], ["currencies.code"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_number"),
    )

    op.create_table(
        "audit_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("login", sa.String(length=50), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity", sa.String(length=100), nullable=True),
        sa.Column("entity_id", sa.String(length=100), nullable=True),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ip_address", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "opening_balances",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(20, 2), nullable=False),
        sa.Column("corrections_amount", sa.Numeric(20, 2), nullable=False),
        sa.Column("is_corrected", sa.Boolean(), nullable=False),
        sa.Column("calculated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("fx_deal_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("currency_code", sa.String(length=3), nullable=False),
        sa.Column("amount", sa.Numeric(20, 2), nullable=False),
        sa.Column("value_date", sa.Date(), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("direction", sa.String(length=3), nullable=False),
        sa.Column("processing_date", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["currency_code"], ["currencies.code"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "corrections",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("opening_balance_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount", sa.Numeric(20, 2), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["opening_balance_id"], ["opening_balances.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "positions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("opening_balance_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(20, 2), nullable=False),
        sa.ForeignKeyConstraint(["opening_balance_id"], ["opening_balances.id"]),
        sa.ForeignKeyConstraint(["payment_id"], ["payments.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    _insert_bootstrap_data()


def downgrade() -> None:
    op.drop_table("positions")
    op.drop_table("corrections")
    op.drop_table("payments")
    op.drop_table("opening_balances")
    op.drop_table("audit_log")
    op.drop_table("accounts")
    op.drop_table("users")
    op.drop_table("currencies")


def _insert_bootstrap_data() -> None:
    op.bulk_insert(
        sa.table(
            "currencies",
            sa.column("code", sa.String),
            sa.column("name", sa.String),
            sa.column("decimal_places", sa.SmallInteger),
        ),
        [
            {"code": "USD", "name": "Доллар США", "decimal_places": 2},
            {"code": "EUR", "name": "Евро", "decimal_places": 2},
            {"code": "RUB", "name": "Российский рубль", "decimal_places": 2},
            {"code": "CNY", "name": "Китайский юань", "decimal_places": 2},
            {"code": "GBP", "name": "Британский фунт", "decimal_places": 2},
        ],
    )

    op.bulk_insert(
        sa.table(
            "users",
            sa.column("id", postgresql.UUID),
            sa.column("login", sa.String),
            sa.column("password_hash", sa.String),
            sa.column("full_name", sa.String),
            sa.column("role", sa.String),
            sa.column("is_active", sa.Boolean),
        ),
        [
            {
                "id": ADMIN_ID,
                "login": "admin",
                "password_hash": "$2b$12$ND1GoKf9Fkc3EF.XL.fncOTEolIjUlX9vuQp1i/uAct9FOmbCHmie",
                "full_name": "Главный Администратор",
                "role": "ADMIN",
                "is_active": True,
            },
            {
                "id": POSITIONER_01_ID,
                "login": "positioner01",
                "password_hash": "$2b$12$BVrtd5G1F0P39zHld9PL3uodsEbfACk43HXkHNwEvdupUKwOV39ea",
                "full_name": "Иванов Иван Иванович",
                "role": "POSITIONER",
                "is_active": True,
            },
            {
                "id": POSITIONER_02_ID,
                "login": "positioner02",
                "password_hash": "$2b$12$mNIqvladijda9vJfvR8qLOwMck5rNjZ91kUog/nD7BBk8ig.woXdG",
                "full_name": "Петрова Анна Сергеевна",
                "role": "POSITIONER",
                "is_active": True,
            },
            {
                "id": TRADER_01_ID,
                "login": "trader01",
                "password_hash": "$2b$12$ipJ8VIvAVeembDS.hvf0V.dxdqFZaQOISX6xm/OMp3XmQalMD8esW",
                "full_name": "Сидоров Алексей Петрович",
                "role": "TRADER",
                "is_active": True,
            },
            {
                "id": TRADER_02_ID,
                "login": "trader02",
                "password_hash": "$2b$12$nvyr9XClTuy08SRqcOW40Oj2yOWVTHPt1So6vBCCe9QR0DX3BMWs2",
                "full_name": "Козлова Мария Дмитриевна",
                "role": "TRADER",
                "is_active": True,
            },
        ],
    )

    op.bulk_insert(
        sa.table(
            "accounts",
            sa.column("id", postgresql.UUID),
            sa.column("account_number", sa.String),
            sa.column("name", sa.String),
            sa.column("currency_code", sa.String),
            sa.column("correspondent_bank", sa.String),
            sa.column("limit", sa.Numeric),
            sa.column("is_active", sa.Boolean),
        ),
        [
            {
                "id": USD_ACCOUNT_ID,
                "account_number": "30111840000000001001",
                "name": "Ностро USD в Citibank",
                "currency_code": "USD",
                "correspondent_bank": "Citibank N.A., New York",
                "limit": 500000,
                "is_active": True,
            },
            {
                "id": EUR_ACCOUNT_ID,
                "account_number": "30111978000000001002",
                "name": "Ностро EUR в Deutsche Bank",
                "currency_code": "EUR",
                "correspondent_bank": "Deutsche Bank AG, Frankfurt",
                "limit": 300000,
                "is_active": True,
            },
            {
                "id": CNY_ACCOUNT_ID,
                "account_number": "30111156000000001003",
                "name": "Ностро CNY в Bank of China",
                "currency_code": "CNY",
                "correspondent_bank": "Bank of China, Beijing",
                "limit": 2000000,
                "is_active": True,
            },
            {
                "id": GBP_ACCOUNT_ID,
                "account_number": "30111826000000001004",
                "name": "Ностро GBP в Barclays",
                "currency_code": "GBP",
                "correspondent_bank": "Barclays Bank PLC, London",
                "limit": 200000,
                "is_active": True,
            },
        ],
    )

    op.execute(
        sa.text(
            """
            INSERT INTO opening_balances (
                id,
                account_id,
                date,
                amount,
                corrections_amount,
                is_corrected,
                calculated_at
            )
            VALUES
                ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb1', :usd_account_id, CURRENT_DATE, 1200000.00, 0, false, NULL),
                ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb2', :eur_account_id, CURRENT_DATE, 850000.00, 0, false, NULL),
                ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb3', :cny_account_id, CURRENT_DATE, 5000000.00, 0, false, NULL),
                ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb4', :gbp_account_id, CURRENT_DATE, 400000.00, 0, false, NULL)
            """
        ).bindparams(
            usd_account_id=USD_ACCOUNT_ID,
            eur_account_id=EUR_ACCOUNT_ID,
            cny_account_id=CNY_ACCOUNT_ID,
            gbp_account_id=GBP_ACCOUNT_ID,
        )
    )
