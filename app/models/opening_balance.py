import uuid
from sqlalchemy import Column, Numeric, Date, Boolean, ForeignKey
from sqlalchemy import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class OpeningBalance(Base):
    __tablename__ = "входящий_остаток"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_счета = Column(UUID(as_uuid=True), ForeignKey("счета.id"), nullable=False)
    дата = Column(Date, nullable=False)
    сумма = Column(Numeric(20, 2), nullable=False, default=0)
    сумма_корректировок = Column(Numeric(20, 2), nullable=False, default=0)
    скорректирован = Column(Boolean, nullable=False, default=False)
    дата_расчета = Column(TIMESTAMP(timezone=True), nullable=True)

    счет = relationship("Account", back_populates="остатки")
    позиции = relationship("Position", back_populates="входящий_остаток")
    корректировки = relationship("Correction", back_populates="входящий_остаток")
