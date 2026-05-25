import uuid
from sqlalchemy import Column, Numeric, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Position(Base):
    __tablename__ = "позиция"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_платежа = Column(UUID(as_uuid=True), ForeignKey("платежи.id"), nullable=False)
    id_входящего_остатка = Column(
        UUID(as_uuid=True), ForeignKey("входящий_остаток.id"), nullable=False
    )
    дата = Column(Date, nullable=False)
    сумма = Column(Numeric(20, 2), nullable=False)

    платеж = relationship("Payment", back_populates="позиции")
    входящий_остаток = relationship("OpeningBalance", back_populates="позиции")
