import uuid
from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.database import Base


class AuditLog(Base):
    __tablename__ = "журнал_аудита"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    пользователь_id = Column(UUID(as_uuid=True), ForeignKey("пользователи.id"), nullable=True)
    логин = Column(String(50), nullable=True)
    действие = Column(String(100), nullable=False)
    сущность = Column(String(100), nullable=True)
    сущность_id = Column(String(100), nullable=True)
    детали = Column(JSONB, nullable=True)
    ip_адрес = Column(String(50), nullable=True)
    дата_время = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
