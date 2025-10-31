from typing import Optional

from pydantic import BaseModel, Field

from src.db.models import CurrencyEnum, StatusEnum


class PaymentBase(BaseModel):
    amount: float = Field(...)
    currency: CurrencyEnum = Field(default=CurrencyEnum.RUB)
    status: StatusEnum = Field(default=StatusEnum.PAID)
    external_id: str = Field(...)
    client_id: int = Field(...)


class PaymentCreate(PaymentBase):
    currency: Optional[CurrencyEnum] = None
    status: Optional[StatusEnum] = None
    external_id: Optional[str] = None
