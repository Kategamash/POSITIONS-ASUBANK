import uuid
from sqlalchemy import Column, String, Numeric, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

DIRECTION_IN = "IN"
DIRECTION_OUT = "OUT"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fx_deal_id = Column(UUID(as_uuid=True), nullable=True)
    currency_code = Column(String(3), ForeignKey("currencies.code"), nullable=False)
    amount = Column(Numeric(20, 2), nullable=False)
    value_date = Column(Date, nullable=False)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    direction = Column(String(3), nullable=False)  # IN / OUT
    processing_date = Column(Date, nullable=False)

    currency = relationship("Currency")
    account = relationship("Account", back_populates="payments")
    positions = relationship("Position", back_populates="payment")
