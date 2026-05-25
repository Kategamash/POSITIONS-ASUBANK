import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

ROLE_TRADER = "TRADER"
ROLE_POSITIONER = "POSITIONER"
ROLE_ADMIN = "ADMIN"

ROLES = [ROLE_TRADER, ROLE_POSITIONER, ROLE_ADMIN]


class User(Base):
    __tablename__ = "пользователи"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    логин = Column(String(50), nullable=False, unique=True)
    хэш_пароля = Column(String(200), nullable=False)
    полное_имя = Column(String(200), nullable=False)
    роль = Column(String(20), nullable=False)  # TRADER / POSITIONER / ADMIN
    активен = Column(Boolean, nullable=False, default=True)
    дата_создания = Column(TIMESTAMP(timezone=True), server_default=func.now())
