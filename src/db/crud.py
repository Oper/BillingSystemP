from datetime import datetime, date
from typing import Optional, Sequence

from sqlalchemy import select, or_, func, delete, desc, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.db.models import Client, Tariff, Payment, Accrual, StatusClientEnum
from src.models.clients import ClientCreate, ClientUpdate
from src.models.payments import PaymentCreate
from src.models.tariffs import TariffCreate
from src.models.accruals import AccrualCreate


def create_client(db: Session, client_data: ClientCreate) -> Client | None:
    """
    Синхронно добавляет нового клиента в базу данных.

    :param db: Активная синхронная сессия базы данных.
    :param client_data: Объект Pydantic с данными нового клиента.
    :return: Созданный объект клиента (модель SQLAlchemy).
    """
    db_client_data = client_data.model_dump()
    db_client = Client(**db_client_data)
    try:
        db.add(db_client)
        db.commit()
        return db_client
    except SQLAlchemyError as e:
        db.rollback()
        return None


def bulk_create_clients(db: Session, clients_list: list[ClientCreate]):
    if not clients_list:
        return

    data = [c.model_dump() for c in clients_list]

    try:
        db.execute(insert(Client), data)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Критическая ошибка базы данных: {e}")
        raise e


def delete_client(db: Session, client_id: int) -> bool:
    """
        Синхронно удаляет клиента в базе данных.

        :param db: Активная синхронная сессия базы данных.
        :param client_id: Идентификатор клиента.
        :return: True, если клиент был успешно удален, False в противном случае.
        """
    # 1. Формируем запрос на удаление
    # DELETE FROM clients WHERE id = :client_id
    try:
        stmt = delete(Client).where(Client.id == client_id)

        # 2. Выполняем запрос
        db.execute(stmt)

        # 3. Фиксируем изменения
        db.commit()

        # rowcount > 0 означает, что была удалена хотя бы одна запись
        return True

    except SQLAlchemyError as e:
        db.rollback()
        return False


def delete_tariff(db: Session, tariff_id: int) -> bool:
    """
            Синхронно удаляет тариф в базе данных.

            :param db: Активная синхронная сессия базы данных.
            :param tariff_id: Идентификатор клиента.
            :return: True, если клиент был успешно удален, False в противном случае.
            """
    # 1. Формируем запрос на удаление
    # DELETE FROM clients WHERE id = :client_id
    try:
        stmt = delete(Tariff).where(Tariff.id == tariff_id)

        # 2. Выполняем запрос
        db.execute(stmt)

        # 3. Фиксируем изменения
        db.commit()

        # rowcount > 0 означает, что была удалена хотя бы одна запись
        return True

    except SQLAlchemyError as e:
        db.rollback()
        return False


def get_client_by_id(db: Session, client_id: int) -> Optional[Client]:
    """
    Синхронно получает одного клиента по его уникальному ID.

    :param db: Активная синхронная сессия базы данных.
    :param client_id: Уникальный ID клиента.
    :return: Объект клиента или None, если клиент не найден.
    """
    # Формируем запрос: SELECT * FROM clients WHERE id = :client_id
    stmt = select(Client).where(Client.id == client_id)

    # Выполняем запрос и возвращаем первый найденный объект (или None)
    result = db.execute(stmt)
    return result.scalars().first()


def get_client_by_pa(db: Session, client_pa: int) -> Optional[Client]:
    """
    Синхронно получает одного клиента по его уникальному Лицевому счету.

    :param db: Активная синхронная сессия базы данных.
    :param client_pa: Уникальный PA (personal account) клиента.
    :return: Объект клиента или None, если клиент не найден.
    """
    # Формируем запрос: SELECT * FROM clients WHERE personal_account = :client_pa
    stmt = select(Client).where(Client.personal_account == client_pa)

    # Выполняем запрос и возвращаем первый найденный объект (или None)
    result = db.execute(stmt)
    return result.scalars().first()


def update_client(db: Session, client_id: int, client_data: ClientUpdate) -> Optional[Client]:
    """
    Синхронно обновляет данные существующего клиента.

    :param db: Активная синхронная сессия базы данных.
    :param client_id: ID клиента, которого нужно обновить.
    :param client_data: Объект Pydantic с новыми данными (только те, что нужно изменить).
    :return: Обновленный объект клиента или None, если клиент не найден.
    """
    # 1. Получаем клиента, которого будем обновлять
    db_client = get_client_by_id(db, client_id)

    if db_client is None:
        return None  # Клиент не найден

    # 2. Преобразуем Pydantic-объект в словарь, игнорируя поля, которые равны None
    update_data = client_data.model_dump(exclude_none=True)

    # 3. Обновляем атрибуты объекта SQLAlchemy
    for key, value in update_data.items():
        # Используем setattr для динамического обновления полей
        setattr(db_client, key, value)

    # 4. Фиксируем изменения в базе
    db.commit()
    # await db.refresh(db_client) # Можно обновить, чтобы убедиться в актуальности данных

    return db_client


def get_clients(db: Session, skip: int = 0, limit: int = 1000) -> Sequence[Client]:
    """
    Синхронно получает список клиентов с возможностью пагинации.

    :param db: Активная синхронная сессия базы данных.
    :param skip: Количество записей, которое нужно пропустить (смещение).
    :param limit: Максимальное количество записей для возврата.
    :return: Список объектов клиентов (моделей SQLAlchemy).
    """
    # 1. Формируем синхронный запрос: SELECT * FROM clients
    stmt = select(Client).offset(skip).limit(limit)

    # 2. Выполняем запрос
    result = db.execute(stmt)

    # 3. Получаем все результаты (scalar_all)
    # .scalars() возвращает объекты модели Client, а не кортежи
    return result.scalars().all()


def search_clients(db: Session, search_term: str) -> Sequence[Client]:
    """
    Синхронно ищет клиентов по Л/С (если цифры) или по частичному совпадению
    ФИО или Адреса (без учета регистра).
    """
    search_pattern = f"%{search_term}%"

    if search_term.isdigit():
        stmt = select(Client).where(Client.personal_account.like(search_pattern))
    else:
        stmt = select(Client).where(
            or_(
                Client.full_name.ilike(search_pattern),
                Client.address.ilike(search_pattern)
            )
        )

    result = db.execute(stmt)

    return result.scalars().all()


def create_tariff(db: Session, tariff_data: TariffCreate) -> Tariff | None:
    """Добавляет новый тариф."""
    try:
        db_tariff = Tariff(**tariff_data.model_dump())
        db.add(db_tariff)
        db.commit()
        return db_tariff
    except SQLAlchemyError as e:
        db.rollback()
        return None


def get_tariff_by_name(db: Session, name: str) -> Optional[Tariff]:
    """Находит тариф по имени."""
    stmt = select(Tariff).where(func.lower(Tariff.name) == func.lower(name))
    result = db.execute(stmt)
    return result.scalars().first()


def get_tariff_by_id(db: Session, tariff_id: int) -> Tariff | None:
    """
        Синхронно получает один тариф по его уникальному ID.

        :param db: Активная синхронная сессия базы данных.
        :param tariff_id: Уникальный ID тарифа.
        :return: Объект клиента или None, если клиент не найден.
        """
    # Формируем запрос: SELECT * FROM clients WHERE id = :client_id
    stmt = select(Tariff).where(Tariff.id == tariff_id)

    # Выполняем запрос и возвращаем первый найденный объект (или None)
    result = db.execute(stmt)
    return result.scalars().first()


def get_tariffs(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Tariff]:
    """Получение списка Тарифов"""
    stmt = select(Tariff).offset(skip).limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()


def apply_monthly_charge(db: Session, client_id: int) -> Optional[Client]:
    """
    Рассчитывает ежемесячную плату и вычитает ее из баланса (БЕЗ коммита).
    """
    client = get_client_by_id(db, client_id)

    # В 2026 году лучше проверять статус через Enum или явное сравнение
    if client is None or client.status != StatusClientEnum.CONNECTING:
        return None

    tariff = get_tariff_by_name(db, client.tariff)
    if tariff is None:
        # Логирование вместо простого принта — хороший тон в 2026
        # logger.warning(f"Тариф '{client.tariff}' не найден для ID {client_id}")
        return client

    # Вычитаем стоимость
    client.balance -= tariff.monthly_price

    # db.flush() синхронизирует состояние с БД, но не закрывает транзакцию.
    # Это позволяет другим запросам в этой же сессии видеть обновленный баланс.
    db.flush()

    return client


def apply_daily_charge(db: Session, client_id: int, count_days: int) -> Optional[Client]:
    """
    Рассчитывает пропорциональную оплату (БЕЗ коммита).
    """
    client = get_client_by_id(db, client_id)
    if client is None or client.status != StatusClientEnum.CONNECTING:
        return None

    tariff = get_tariff_by_name(db, client.tariff)
    if tariff is None:
        return client

    # Расчет суммы (Вариант А: Точный финансовый через Decimal)
    # Чтобы не терять копейки, сначала умножаем цену на дни, затем делим на 30
    charge_amount = (tariff.monthly_price * count_days) / 30

    # Округляем до 2 знаков после запятой
    charge_amount = round(charge_amount, 2)

    # Обновляем баланс
    client.balance -= float(charge_amount)  # или оставить Decimal, если поле Numeric

    # Синхронизируем состояние, но оставляем транзакцию открытой
    db.flush()

    return client


def set_client_activity(db: Session, client_id: int, is_active: bool) -> Optional[Client]:
    """
    Приостанавливает (is_active=False) или возобновляет (is_active=True) обслуживание клиента.
    :param db: Активная синхронная сессия базы данных.
    :param client_id: ID клиента.
    :param is_active: Новый статус активности (True/False).
    :return: Обновленный объект клиента или None.
    """
    client = get_client_by_id(db, client_id)
    if client is None:
        return None

    # Обновляем поле is_active
    client.is_active = is_active

    # Фиксируем изменения
    db.commit()
    # await db.refresh(client)

    return client


def set_client_status(db: Session, client_id: int, status: StatusClientEnum) -> Optional[Client]:
    """
    Устанавливает статус абонента.
    :param db: Активная синхронная сессия базы данных.
    :param client_id: ID клиента.
    :param status: Новый статус активности (Подключен/Отключен/Приостановлен).
    :return: Обновленный объект клиента или None.
    """
    client = get_client_by_id(db, client_id)
    if client is None:
        return None

    # Обновляем поле is_active
    client.status = status
    client.status_date = datetime.now()
    db.commit()

    # Фиксируем изменения
    db.commit()
    # await db.refresh(client)

    return client


def create_payment(db: Session, payment: PaymentCreate) -> Payment | None:
    """
        Синхронно добавляет новый платеж в базу данных.

        :param db: Активная синхронная сессия базы данных.
        :param payment: Объект Pydantic с данными нового платежа.
        :return: Созданный объект платежа (модель SQLAlchemy).
        """

    db_payment_data = payment.model_dump()

    db_payment = Payment(**db_payment_data)
    try:
        db.add(db_payment)
        db.commit()
        return db_payment
    except SQLAlchemyError as e:
        db.rollback()
        return None

def get_payment_by_id(db: Session, payment_id: int) -> Optional[Payment]:
    """
    Синхронно получает один платеж по его уникальному ID.

    :param db: Активная синхронная сессия базы данных.
    :param payment_id: Уникальный ID платежа.
    :return: Объект платежа или None, если платеж не найден.
    """

    stmt = select(Payment).where(Payment.id == payment_id)

    result = db.execute(stmt)
    return result.scalars().first()


def get_payments(db: Session, skip: int = 0, limit: int = 100) -> Sequence[Payment]:
    """
    Синхронно получает список платежей с возможностью пагинации.

    :param db: Активная синхронная сессия базы данных.
    :param skip: Количество записей, которое нужно пропустить (смещение).
    :param limit: Максимальное количество записей для возврата.
    :return: Список объектов платежей (моделей SQLAlchemy).
    """
    # 1. Формируем синхронный запрос: SELECT * FROM clients
    stmt = select(Payment).offset(skip).limit(limit)

    # 2. Выполняем запрос
    result = db.execute(stmt)

    # 3. Получаем все результаты (scalar_all)
    # .scalars() возвращает объекты модели Payment, а не кортежи
    return result.scalars().all()


def get_debtors_report(db: Session) -> Sequence[Client]:
    """Формирует отчет: получает список всех клиентов, чей баланс меньше 0 (должники).
    :param db: Активная синхронная сессия базы данных.
    """
    stmt = select(Client).where(Client.balance < 0).order_by(Client.balance)
    result = db.execute(stmt)
    return result.scalars().all()


def get_payments_by_client(db: Session, client_id: int) -> Sequence[Payment]:
    """
    Синхронно получает список платежей с Клиента.

    :param client_id: ID Клиента.
    :param db: Активная синхронная сессия базы данных.
    :return: Список объектов платежей (моделей SQLAlchemy).
    """
    stmt = select(Payment).where(Payment.client_id == client_id)
    result = db.execute(stmt)
    return result.scalars().all()


def get_last_payment_by_client(db: Session, client_id: int) -> Optional[Payment]:
    """
        Синхронно получает последний платеж Клиента.

        :param client_id: ID Клиента.
        :param db: Активная синхронная сессия базы данных.
        :return: Объект платежа (моделей SQLAlchemy).
        """
    stmt = select(Payment).where(Payment.client_id == client_id).order_by(desc(Payment.id)).limit(1)
    result = db.execute(stmt)
    return result.scalar_one_or_none()


def get_payments_in_range(db: Session, start_date: datetime, end_date: datetime) -> Sequence[Payment]:
    query = (
        select(Payment)
        .where(Payment.created_at.between(start_date, end_date))
        .order_by(Payment.created_at.asc())
    )
    result = db.execute(query)
    return result.scalars().all()


def get_accruals_by_client(db: Session, client_id: int) -> Sequence[Accrual]:
    """
        Синхронно получает список начислений Клиента.

        :param client_id: ID Клиента.
        :param db: Активная синхронная сессия базы данных.
        :return: Список объектов платежей (моделей SQLAlchemy).
        """
    stmt = select(Accrual).where(Accrual.client_id == client_id)
    result = db.execute(stmt)
    return result.scalars().all()


def get_last_accrual_by_client(db: Session, client_id: int) -> Optional[Accrual]:
    """
        Синхронно получает последний платеж Клиента.

        :param client_id: ID Клиента.
        :param db: Активная синхронная сессия базы данных.
        :return: Объект платежа (моделей SQLAlchemy).
        """
    stmt = select(Accrual).where(Accrual.client_id == client_id).order_by(desc(Accrual.id)).limit(1)
    result = db.execute(stmt)
    return result.scalar_one_or_none()


def create_accrual(db: Session, accrual: AccrualCreate) -> Accrual | None:
    """
        Синхронно добавляет новые начисление в базу данных.

        :param db: Активная синхронная сессия базы данных.
        :param accrual: Объект Pydantic с данными начисления.
        :return: Созданный объект платежа (модель SQLAlchemy).
        """

    db_accrual_data = accrual.model_dump()

    db_accrual = Accrual(**db_accrual_data)
    try:
        db.add(db_accrual)
        db.commit()
        return db_accrual
    except SQLAlchemyError as e:
        db.rollback()
        return None


def create_accrual_daily(db: Session, client_id: int, count_days: int, accrual_date: datetime) -> Optional[Accrual]:
    """
    Синхронно добавляет начисление за неполный месяц.
    """
    client = get_client_by_id(db, client_id)
    if client is None or client.is_active == 0:
        return None

    tariff = get_tariff_by_name(db, client.tariff)
    if tariff is None:
        return None

    # Точный расчет суммы (сначала умножаем, потом делим)
    # Используем round(..., 2) для денежного формата
    charge_amount = round((tariff.monthly_price * count_days) / 30, 2)

    # Используем Pydantic v2 .model_dump()
    accrual_data = AccrualCreate(
        amount=float(charge_amount),
        client_id=client.id,
        accrual_date=accrual_date
    )

    # Прямое создание без лишних вложенных вызовов
    accrual_db = Accrual(**accrual_data.model_dump())

    db.add(accrual_db)
    db.flush()  # Синхронизируем, но не закрываем транзакцию

    return accrual_db


def create_accrual_monthly(db: Session, client: Client, tariff: Tariff, accrual_date: date) -> Optional[Accrual]:
    """
    Создает запись о начислении на основе уже имеющихся объектов клиента и тарифа.
    """
    try:
        # Используем Pydantic схему для валидации (Pydantic v2 .model_dump())
        accrual_data = AccrualCreate(
            amount=tariff.monthly_price,
            client_id=client.id,
            accrual_date=accrual_date
        )

        # Создаем модель SQLAlchemy
        accrual_db = Accrual(**accrual_data.model_dump())

        db.add(accrual_db)
        db.flush()  # Отправляем в БД, но не фиксируем (commit будет в конце цикла)
        return accrual_db

    except Exception as e:
        print(f"Ошибка создания записи начисления: {e}")
        return None


def clear_db_clients(db: Session):
    """
    Удаление базы клиентов.

    :param db: Активная синхронная сессия базы данных.
    """
    db.execute(delete(Client))
    db.commit()
