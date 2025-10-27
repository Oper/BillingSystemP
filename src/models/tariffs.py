from pydantic import BaseModel, Field


class TariffBase(BaseModel):
    name: str = Field(..., description="Название тарифа.")
    monthly_price: float = Field(..., description="Ежемесячная стоимость.")


class TariffCreate(TariffBase):
    pass


class TariffInDB(TariffBase):
    id: int
    is_active: int

    class Config:
        from_attributes = True