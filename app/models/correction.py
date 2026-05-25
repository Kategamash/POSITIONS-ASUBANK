import uuid
from sqlalchemy import Column, Numeric, String, ForeignKey, Text
from sqlalchemy import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Correction(Base):
    __tablename__ = "корректировки"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_входящего_остатка = Column(
        UUID(as_uuid=True), ForeignKey("входящий_остаток.id"), nullable=False
    )
    пользователь_id = Column(
        UUID(as_uuid=True), ForeignKey("пользователи.id"), nullable=False
    )
    сумма = Column(Numeric(20, 2), nullable=False)
    комментарий = Column(Text, nullable=True)
    дата_время = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    входящий_остаток = relationship("OpeningBalance", back_populates="корректировки")
    пользователь = relationship("User")
