import uuid
from sqlalchemy import Column, Numeric, Date, Boolean, ForeignKey
from sqlalchemy import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class OpeningBalance(Base):
    __tablename__ = "opening_balances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    date = Column(Date, nullable=False)
    amount = Column(Numeric(20, 2), nullable=False, default=0)
    corrections_amount = Column(Numeric(20, 2), nullable=False, default=0)
    is_corrected = Column(Boolean, nullable=False, default=False)
    calculated_at = Column(TIMESTAMP(timezone=True), nullable=True)

    account = relationship("Account", back_populates="opening_balances")
    positions = relationship("Position", back_populates="opening_balance")
    corrections = relationship("Correction", back_populates="opening_balance")
