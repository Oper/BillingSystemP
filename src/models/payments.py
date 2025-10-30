from pydantic import BaseModel, Field

from src.db.models import CurrencyEnum, StatusEnum


class PaymentBase(BaseModel):
    amount: float = Field(...)
    currency: CurrencyEnum = Field(CurrencyEnum.RUB)
    status: StatusEnum = Field(...)
    external_id: str = Field(...)
    client_id: int = Field(...)