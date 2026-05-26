from pydantic import BaseModel


class CurrencyBase(BaseModel):
    code: str
    name: str
    decimal_places: int = 2


class CurrencyCreate(CurrencyBase):
    pass


class CurrencyRead(CurrencyBase):
    model_config = {"from_attributes": True}
