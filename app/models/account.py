import uuid
from sqlalchemy import Column, String, Numeric, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Account(Base):
    __tablename__ = "счета"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    номер_счета = Column(String(20), nullable=False, unique=True)
    наименование = Column(String(200), nullable=False)
    код_валюты = Column(String(3), ForeignKey("валюта.код"), nullable=False)
    банк_корреспондент = Column(String(200), nullable=False)
    лимит = Column(Numeric(20, 2), nullable=True)
    активен = Column(Boolean, nullable=False, default=True)

    валюта = relationship("Currency")
    остатки = relationship("OpeningBalance", back_populates="счет")
    платежи = relationship("Payment", back_populates="счет")
