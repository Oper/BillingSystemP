from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ClientBase(BaseModel):
    """Базовая модель для данных клиента."""
    personal_account: int = Field(..., description="Лицевой счет абонента.")
    full_name: str = Field(..., description='Полное ФИО клиента.', min_length=3)
    address: str = Field(..., description='Адрес подключения.', min_length=3)
    phone_number: str = Field(..., description='Номер телефона.', min_length=5)
    tariff: str = Field(..., description='Название выбранного тарифа.')
    balance: float = Field(0.0, description='Начальный баланс.')


class ClientCreate(ClientBase):
    """Модель для создания клиента (наследует ClientBase)."""
    pass


class ClientForPayments(ClientBase):
    is_active: int


class ClientCard(ClientBase):
    client_id: int
    is_active: int
    connection_date: datetime
    passport: Optional[dict] = None


class ClientUpdate(ClientBase):
    """Модель для обновления клиента (все поля необязательны для обновления)."""
    personal_account: Optional[int] = None
    full_name: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    tariff: Optional[str] = None
    balance: Optional[float] = None
    is_active: Optional[int] = None
    passport: Optional[dict] = None


class ClientInDB(ClientBase):
    """Модель данных клиента, как они хранятся в БД (с ID и датами)."""
    id: int
    connection_date: datetime
    is_active: int

    model_config = ConfigDict(
        from_attributes=True
    )
    # class Config:
    #     from_attributes = True
