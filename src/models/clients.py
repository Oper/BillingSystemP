from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

class ClientBase(BaseModel):
    """Базовая модель для данных клиента.

    """
    full_name: str = Field(..., description='Полное ФИО клиента.')
    address: str = Field(..., description='Адрес подключения.')
    phone_number: Optional[str] = Field(..., description='Номер телефона.')
    tariff: str = Field(..., description='Название выбранного тарифа.')
    balance: float = Field(0.0, description='Начальный баланс.')

class ClientCreate(ClientBase):
    """Модель для создания клиента (наследует ClientBase)."""
    pass


class ClientUpdate(ClientBase):
    """Модель для обновления клиента (все поля необязательны для обновления)."""
    full_name: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    tariff: Optional[str] = None
    balance: Optional[float] = None
    is_active: Optional[int] = None


class ClientInDB(ClientBase):
    """Модель данных клиента, как они хранятся в БД (с ID и датами)."""
    id: int
    connection_date: datetime
    is_active: int

    class Config:
        from_attributes = True