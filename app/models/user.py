"""Зеркало пользователей IdP.

Идентификатор пользователя берётся из IdP (sub/user_id). Локальные
поля password_hash/role оставлены опциональными, чтобы не ломать
исторические таблицы, но не используются: реальная аутентификация и
управление ролями выполняются Identity Provider.
"""

import uuid

from sqlalchemy import TIMESTAMP, Boolean, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.database import Base

ROLE_TRADER = "TRADER"
ROLE_POSITIONER = "POSITIONER"
ROLE_AUDITOR = "AUDITOR"
ROLE_ADMIN = "ADMIN"

ROLES = [ROLE_TRADER, ROLE_POSITIONER, ROLE_AUDITOR, ROLE_ADMIN]


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    login = Column(String(200), nullable=False, unique=True)
    password_hash = Column(String(200), nullable=True)  # legacy, не используется
    full_name = Column(String(200), nullable=False)
    role = Column(String(20), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
