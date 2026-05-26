import uuid
from sqlalchemy import Column, String, Numeric, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_number = Column(String(20), nullable=False, unique=True)
    name = Column(String(200), nullable=False)
    currency_code = Column(String(3), ForeignKey("currencies.code"), nullable=False)
    correspondent_bank = Column(String(200), nullable=False)
    limit = Column(Numeric(20, 2), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    currency = relationship("Currency")
    opening_balances = relationship("OpeningBalance", back_populates="account")
    payments = relationship("Payment", back_populates="account")
