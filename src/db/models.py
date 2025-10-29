import enum
from datetime import datetime
from typing import List

from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import BaseModel


class StatusEnum(str, enum.Enum):
    PENDING = "Ожидает"
    PAID = "Оплачен"
    FAILED = "Неудачный"
    REFUNDED = "Возвращен"

class CurrencyEnum(str, enum.Enum):
    RUB = "Рубль"
    USD = "Доллар"


class Client(BaseModel):
    """Модель клиента.
    """
    __tablename__ = 'clients'
    personal_account: Mapped[int] = mapped_column(unique=True)
    full_name: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column(unique=True)
    phone_number: Mapped[str] = mapped_column(unique=True)
    tariff: Mapped[str] = mapped_column(nullable=False)
    connection_date: Mapped[datetime] = mapped_column(server_default=func.now())
    balance: Mapped[float] = mapped_column(default=0.0)
    is_active: Mapped[bool] = mapped_column(default=True)
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f'Client (id={self.id}, name={self.full_name}, balance={self.balance}, is_active={self.is_active})'


class Service(BaseModel):
    """Модель услуг TODO"""
    __tablename__ = 'services'
    service_name: Mapped[str] = mapped_column(unique=True)
    service_price: Mapped[float] = mapped_column(default=0.0)

    def __repr__(self):
        return f'Service (name={self.service_name}, price={self.service_price})'


class Tariff(BaseModel):
    """Модель тарифов"""
    __tablename__ = 'tariffs'
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    monthly_price: Mapped[float] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    def __repr__(self):
        return f"Tariff(id={self.id}, name='{self.name}', price={self.monthly_price})"

class Payment(BaseModel):
    """Модель платежей"""
    __tablename__ = 'payments'
    amount: Mapped[float] = mapped_column(default=0.0)
    currency: Mapped[CurrencyEnum] = mapped_column(default=CurrencyEnum.RUB)
    status: Mapped[StatusEnum] = mapped_column(nullable=False)
    external_id: Mapped[str | None] = mapped_column(unique=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    client: Mapped["Client"] = relationship("Client", back_populates="payments")