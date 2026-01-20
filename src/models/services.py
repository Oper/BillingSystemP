from pydantic import BaseModel, Field


class ServiceBase(BaseModel):
    service_name: str = Field(..., description="Название услуги.")
    service_price: float = Field(..., description="Cтоимость.")


class ServiceCreate(ServiceBase):
    pass


class ServiceInDB(ServiceBase):
    id: int
    is_active: int

    class Config:
        from_attributes = True