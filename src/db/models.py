from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import BaseModel


class Client(BaseModel):
    """Модель клиента.
    """
    __tablename__='clients'
    full_name: Mapped[str] = mapped_column(unique=True)
    address: Mapped[str] = mapped_column(unique=True)
    phone_number: Mapped[str] = mapped_column(unique=True)
    tariff: Mapped[str] = mapped_column(nullable=False)
    connection_date: Mapped[datetime] = mapped_column(server_default=func.now())
    balance: Mapped[float] = mapped_column(default=0.0)
    is_active: Mapped[bool] = mapped_column(default=True)

    def __repr__(self):
        return f'Client (id={self.id}, name={self.full_name}, balance={self.balance}, is_active={self.is_active})'


class Service(BaseModel):
    __tablename__='services'
    service_name: Mapped[str] = mapped_column(unique=True)
    service_price: Mapped[float] = mapped_column(default=0.0)

    def __repr__(self):
        return f'Service (name={self.service_name}, price={self.service_price})'