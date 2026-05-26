import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

ROLE_TRADER = "TRADER"
ROLE_POSITIONER = "POSITIONER"
ROLE_ADMIN = "ADMIN"

ROLES = [ROLE_TRADER, ROLE_POSITIONER, ROLE_ADMIN]


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    login = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(200), nullable=False)
    full_name = Column(String(200), nullable=False)
    role = Column(String(20), nullable=False)  # TRADER / POSITIONER / ADMIN
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
