from sqlalchemy import Column, String, SmallInteger
from app.database import Base


class Currency(Base):
    __tablename__ = "валюта"

    код = Column(String(3), primary_key=True)
    наименование = Column(String(100), nullable=False)
    знаков_после_запятой = Column(SmallInteger, nullable=False, default=2)
