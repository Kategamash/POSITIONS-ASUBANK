"""Подключение к БД.

Поддерживается два режима:

1. **Локальный**: задайте `DATABASE_URL` (или `LOCAL_DATABASE_URL`) — например
   ``postgresql+psycopg2://positions:positions_password@postgres:5432/positions_asubank``
   и SSH-туннель отключается. Этот режим используется при `docker compose up`.

2. **SSH-туннель к продовой БД**: задайте `USE_SSH_TUNNEL=true` (или не задавайте
   `DATABASE_URL`) и параметры `DB_*` / `SSH_*`. Сохранён для совместимости с
   первоначальной конфигурацией Team 2.
"""

from __future__ import annotations

import os
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


def _resolve_url() -> str:
    explicit = os.getenv("DATABASE_URL") or os.getenv("LOCAL_DATABASE_URL")
    if explicit:
        return explicit

    if str(os.getenv("USE_SSH_TUNNEL", "")).lower() in ("1", "true", "yes"):
        from sshtunnel import SSHTunnelForwarder

        global _tunnel
        _tunnel = SSHTunnelForwarder(
            (settings.SSH_HOST, settings.SSH_PORT),
            ssh_username=settings.SSH_USER,
            ssh_password=settings.SSH_PASSWORD,
            remote_bind_address=("127.0.0.1", settings.DB_PORT),
        )
        _tunnel.start()
        local_port = _tunnel.local_bind_port
        return (
            f"postgresql+psycopg2://{quote_plus(settings.DB_USER)}:{quote_plus(settings.DB_PASSWORD)}"
            f"@127.0.0.1:{local_port}/{settings.DB_NAME}?gssencmode=disable"
        )

    # Дефолт для локального docker-compose.
    return "postgresql+psycopg2://positions:positions_password@postgres:5432/positions_asubank"


_tunnel = None
_DB_URL = _resolve_url()
engine = create_engine(_DB_URL, pool_pre_ping=True, pool_recycle=300)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
