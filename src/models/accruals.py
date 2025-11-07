from datetime import datetime

from pydantic import BaseModel, Field


class AccrualBase(BaseModel):
    amount: float = Field(...)
    accrual_date: datetime
    client_id: int = Field(...)


class AccrualCreate(AccrualBase):
    pass