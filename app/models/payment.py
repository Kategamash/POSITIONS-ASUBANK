import uuid
from sqlalchemy import Column, String, Numeric, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

# Направление платежа
DIRECTION_IN = "IN"
DIRECTION_OUT = "OUT"


class Payment(Base):
    __tablename__ = "платежи"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # ID сделки во внешней системе FX-АСУБАНК
    id_сделки_fx = Column(UUID(as_uuid=True), nullable=True)
    код_валюты = Column(String(3), ForeignKey("валюта.код"), nullable=False)
    сумма = Column(Numeric(20, 2), nullable=False)
    дата_валютирования = Column(Date, nullable=False)
    id_счета = Column(UUID(as_uuid=True), ForeignKey("счета.id"), nullable=False)
    направление = Column(String(3), nullable=False)  # IN / OUT
    дата_обработки = Column(Date, nullable=False)

    валюта = relationship("Currency")
    счет = relationship("Account", back_populates="платежи")
    позиции = relationship("Position", back_populates="платеж")
