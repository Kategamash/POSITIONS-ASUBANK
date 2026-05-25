from pydantic import BaseModel


class CurrencyBase(BaseModel):
    код: str
    наименование: str
    знаков_после_запятой: int = 2


class CurrencyCreate(CurrencyBase):
    pass


class CurrencyRead(CurrencyBase):
    model_config = {"from_attributes": True}
