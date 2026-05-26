import uuid
from sqlalchemy import Column, Numeric, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Position(Base):
    __tablename__ = "positions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=False)
    opening_balance_id = Column(
        UUID(as_uuid=True), ForeignKey("opening_balances.id"), nullable=False
    )
    date = Column(Date, nullable=False)
    amount = Column(Numeric(20, 2), nullable=False)

    payment = relationship("Payment", back_populates="positions")
    opening_balance = relationship("OpeningBalance", back_populates="positions")
