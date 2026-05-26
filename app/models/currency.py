from sqlalchemy import Column, String, SmallInteger
from app.database import Base


class Currency(Base):
    __tablename__ = "currencies"

    code = Column(String(3), primary_key=True)
    name = Column(String(100), nullable=False)
    decimal_places = Column(SmallInteger, nullable=False, default=2)
