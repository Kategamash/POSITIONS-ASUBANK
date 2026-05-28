from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import AliasChoices, BaseModel, Field


class PaymentBase(BaseModel):
    currency_code: str
    amount: Decimal
    value_date: date
    account_id: UUID
    direction: str  # IN / OUT
    processing_date: date


class PaymentCreate(PaymentBase):
    fx_deal_id: Optional[UUID] = None


class PaymentRead(PaymentBase):
    id: UUID
    fx_deal_id: Optional[UUID] = None

    model_config = {"from_attributes": True}


class IncomingPaymentFromFX(BaseModel):
    """Incoming payment from FX-DEAL-MANAGER.

    Можно указывать счёт либо UUID (account_id), либо номером (account_number).
    """

    deal_id: UUID = Field(validation_alias=AliasChoices("deal_id", "dealId", "fx_deal_id", "fxDealId"))
    currency_code: str = Field(validation_alias=AliasChoices("currency_code", "currencyCode"))
    amount: Decimal
    value_date: date = Field(validation_alias=AliasChoices("value_date", "valueDate"))
    direction: str = Field(validation_alias=AliasChoices("direction", "payment_direction", "paymentDirection"))  # IN / OUT
    account_id: Optional[UUID] = Field(default=None, validation_alias=AliasChoices("account_id", "accountId"))
    account_number: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("account_number", "accountNumber", "account_code", "accountCode"),
    )
    correlation_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("correlation_id", "correlationId"),
    )

    model_config = {"populate_by_name": True, "extra": "ignore"}
