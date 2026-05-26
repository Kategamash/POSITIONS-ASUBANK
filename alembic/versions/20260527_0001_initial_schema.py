"""Initial schema and bootstrap data.

Revision ID: 20260527_0001
Revises:
Create Date: 2026-05-27 01:35:00
"""
from typing import Sequence, Union

from alembic import context, op
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
    _create_tables()
    _insert_bootstrap_data()


def downgrade() -> None:
    for table_name in (
        "positions",
        "corrections",
        "payments",
        "opening_balances",
        "audit_log",
        "accounts",
        "users",
        "currencies",
    ):
        _drop_table_if_exists(table_name)


def _create_tables() -> None:
    _create_table_if_missing(
        "currencies",
        lambda: op.create_table(
            "currencies",
            sa.Column("code", sa.String(length=3), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("decimal_places", sa.SmallInteger(), nullable=False),
            sa.PrimaryKeyConstraint("code"),
        ),
    )

    _create_table_if_missing(
        "users",
        lambda: op.create_table(
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
        ),
    )

    _create_table_if_missing(
        "accounts",
        lambda: op.create_table(
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
        ),
    )

    _create_table_if_missing(
        "audit_log",
        lambda: op.create_table(
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
        ),
    )

    _create_table_if_missing(
        "opening_balances",
        lambda: op.create_table(
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
        ),
    )

    _create_table_if_missing(
        "payments",
        lambda: op.create_table(
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
        ),
    )

    _create_table_if_missing(
        "corrections",
        lambda: op.create_table(
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
        ),
    )

    _create_table_if_missing(
        "positions",
        lambda: op.create_table(
            "positions",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("payment_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("opening_balance_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("date", sa.Date(), nullable=False),
            sa.Column("amount", sa.Numeric(20, 2), nullable=False),
            sa.ForeignKeyConstraint(["opening_balance_id"], ["opening_balances.id"]),
            sa.ForeignKeyConstraint(["payment_id"], ["payments.id"]),
            sa.PrimaryKeyConstraint("id"),
        ),
    )


def _insert_bootstrap_data() -> None:
    op.execute(
        sa.text(
            """
            INSERT INTO currencies (code, name, decimal_places)
            VALUES
                ('USD', 'Доллар США', 2),
                ('EUR', 'Евро', 2),
                ('RUB', 'Российский рубль', 2),
                ('CNY', 'Китайский юань', 2),
                ('GBP', 'Британский фунт', 2)
            ON CONFLICT (code) DO NOTHING
            """
        )
    )

    op.execute(
        sa.text(
            """
            INSERT INTO users (id, login, password_hash, full_name, role, is_active)
            VALUES
                (:admin_id, 'admin', '$2b$12$ND1GoKf9Fkc3EF.XL.fncOTEolIjUlX9vuQp1i/uAct9FOmbCHmie', 'Главный Администратор', 'ADMIN', true),
                (:positioner_01_id, 'positioner01', '$2b$12$BVrtd5G1F0P39zHld9PL3uodsEbfACk43HXkHNwEvdupUKwOV39ea', 'Иванов Иван Иванович', 'POSITIONER', true),
                (:positioner_02_id, 'positioner02', '$2b$12$mNIqvladijda9vJfvR8qLOwMck5rNjZ91kUog/nD7BBk8ig.woXdG', 'Петрова Анна Сергеевна', 'POSITIONER', true),
                (:trader_01_id, 'trader01', '$2b$12$ipJ8VIvAVeembDS.hvf0V.dxdqFZaQOISX6xm/OMp3XmQalMD8esW', 'Сидоров Алексей Петрович', 'TRADER', true),
                (:trader_02_id, 'trader02', '$2b$12$nvyr9XClTuy08SRqcOW40Oj2yOWVTHPt1So6vBCCe9QR0DX3BMWs2', 'Козлова Мария Дмитриевна', 'TRADER', true)
            ON CONFLICT (login) DO NOTHING
            """
        ).bindparams(
            admin_id=ADMIN_ID,
            positioner_01_id=POSITIONER_01_ID,
            positioner_02_id=POSITIONER_02_ID,
            trader_01_id=TRADER_01_ID,
            trader_02_id=TRADER_02_ID,
        )
    )

    op.execute(
        sa.text(
            """
            INSERT INTO accounts (
                id,
                account_number,
                name,
                currency_code,
                correspondent_bank,
                "limit",
                is_active
            )
            VALUES
                (:usd_account_id, '30111840000000001001', 'Ностро USD в Citibank', 'USD', 'Citibank N.A., New York', 500000, true),
                (:eur_account_id, '30111978000000001002', 'Ностро EUR в Deutsche Bank', 'EUR', 'Deutsche Bank AG, Frankfurt', 300000, true),
                (:cny_account_id, '30111156000000001003', 'Ностро CNY в Bank of China', 'CNY', 'Bank of China, Beijing', 2000000, true),
                (:gbp_account_id, '30111826000000001004', 'Ностро GBP в Barclays', 'GBP', 'Barclays Bank PLC, London', 200000, true)
            ON CONFLICT (account_number) DO NOTHING
            """
        ).bindparams(
            usd_account_id=USD_ACCOUNT_ID,
            eur_account_id=EUR_ACCOUNT_ID,
            cny_account_id=CNY_ACCOUNT_ID,
            gbp_account_id=GBP_ACCOUNT_ID,
        )
    )

    op.execute(
        sa.text(
            """
            WITH seed_balances(account_number, amount) AS (
                VALUES
                    ('30111840000000001001', 1200000.00::numeric),
                    ('30111978000000001002', 850000.00::numeric),
                    ('30111156000000001003', 5000000.00::numeric),
                    ('30111826000000001004', 400000.00::numeric)
            )
            INSERT INTO opening_balances (
                id,
                account_id,
                date,
                amount,
                corrections_amount,
                is_corrected,
                calculated_at
            )
            SELECT
                CASE seed_balances.account_number
                    WHEN '30111840000000001001' THEN 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb1'::uuid
                    WHEN '30111978000000001002' THEN 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb2'::uuid
                    WHEN '30111156000000001003' THEN 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb3'::uuid
                    WHEN '30111826000000001004' THEN 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb4'::uuid
                END,
                accounts.id,
                CURRENT_DATE,
                seed_balances.amount,
                0,
                false,
                NULL
            FROM seed_balances
            JOIN accounts ON accounts.account_number = seed_balances.account_number
            WHERE NOT EXISTS (
                SELECT 1
                FROM opening_balances existing
                WHERE existing.account_id = accounts.id
                  AND existing.date = CURRENT_DATE
            )
            """
        )
    )


def _create_table_if_missing(table_name: str, create_table) -> None:
    if context.is_offline_mode() or not _table_exists(table_name):
        create_table()


def _drop_table_if_exists(table_name: str) -> None:
    if context.is_offline_mode() or _table_exists(table_name):
        op.drop_table(table_name)


def _table_exists(table_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return table_name in inspector.get_table_names()
