from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, or_, func, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.db.models import Client, Tariff, Payment, Accrual
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
    # 1. Преобразуем объект Pydantic в словарь
    # .model_dump() преобразует Pydantic-объект в обычный словарь Python
    db_client_data = client_data.model_dump()
    # 2. Создаем экземпляр модели SQLAlchemy
    db_client = Client(**db_client_data)
    try:
        # 3. Добавляем объект в сессию и фиксируем изменения в базе
        db.add(db_client)
        db.commit()
        return db_client
        # await db.refresh(db_client) # Обновляем объект, чтобы получить ID
    except SQLAlchemyError as e:
        db.rollback()


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


def get_clients(db: Session, skip: int = 0, limit: int = 100) -> List[Client]:
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


def search_clients(db: Session, search_term: str) -> List[Client]:
    """
    Асинхронно ищет клиентов по частичному совпадению ФИО или Адреса (без учета регистра).

    :param db: Активная асинхронная сессия базы данных.
    :param search_term: Строка для поиска.
    :return: Список объектов клиентов, удовлетворяющих условию поиска.
    """
    # Преобразуем поисковый запрос для использования с оператором LIKE
    search_pattern = f"%{search_term}%"

    # 1. Формируем асинхронный запрос
    # Используем func.lower() для поиска без учета регистра
    # Используем or_() для поиска по двум полям: full_name ИЛИ address
    stmt = select(Client).where(
        or_(
            # Проверяем совпадение ФИО
            func.lower(Client.full_name).like(func.lower(search_pattern)),
            # Проверяем совпадение Адреса
            func.lower(Client.address).like(func.lower(search_pattern))
        )
    )

    # 2. Выполняем запрос
    result = db.execute(stmt)

    # 3. Получаем все результаты
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


def get_tariffs(db: Session, skip: int = 0, limit: int = 100) -> List[Tariff]:
    """Получение списка Тарифов"""
    stmt = select(Tariff).offset(skip).limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()


def apply_monthly_charge(db: Session, client_id: int) -> Optional[Client]:
    """
    Рассчитывает ежемесячную плату для клиента и вычитает ее из баланса.
    :param db: Активная синхронная сессия базы данных.
    :param client_id: ID клиента.
    :return: Обновленный объект клиента или None.
    """
    client = get_client_by_id(db, client_id)
    if client is None or client.is_active == 0:
        return None  # Неактивный или несуществующий клиент не списывается

    # 1. Ищем тариф, чтобы узнать цену
    tariff = get_tariff_by_name(db, client.tariff)
    if tariff is None:
        print(f"⚠️ Тариф '{client.tariff}' для клиента {client.full_name} не найден. Списание невозможно.")
        return client  # Возвращаем клиента без изменений

    charge_amount = tariff.monthly_price

    # 2. Обновляем баланс
    client.balance -= charge_amount

    # 3. Фиксируем изменения
    db.commit()
    # await db.refresh(client)

    return client


def apply_daily_charge(db: Session, client_id: int, count_days: int) -> Optional[Client]:
    """
    Рассчитывает ежедневную оплату для клиента и вычитает ее из баланса.
    :param db: Активная синхронная сессия базы данных.
    :param client_id: ID клиента.
    :param count_days: Количество дней для расчета оплаты.
    :return: Обновленный объект клиента или None.
    """
    client = get_client_by_id(db, client_id)
    if client is None or client.is_active == 0:
        return None  # Неактивный или несуществующий клиент не списывается

    # 1. Ищем тариф, чтобы узнать цену
    tariff = get_tariff_by_name(db, client.tariff)
    if tariff is None:
        print(f"⚠️ Тариф '{client.tariff}' для клиента {client.full_name} не найден. Списание невозможно.")
        return client  # Возвращаем клиента без изменений

    charge_amount = tariff.monthly_price // 30 * count_days

    # 2. Обновляем баланс
    client.balance -= charge_amount

    # 3. Фиксируем изменения
    db.commit()
    # await db.refresh(client)

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

    new_status = 1 if is_active else 0

    # Обновляем поле is_active
    client.is_active = new_status

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


def get_payments(db: Session, skip: int = 0, limit: int = 100) -> List[Payment]:
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


def get_debtors_report(db: Session) -> List[Client]:
    """Формирует отчет: получает список всех клиентов, чей баланс меньше 0 (должники).
    :param db: Активная синхронная сессия базы данных.
    """
    stmt = select(Client).where(Client.balance < 0).order_by(Client.balance)
    result = db.execute(stmt)
    return result.scalars().all()


def get_payments_by_client(db: Session, client_id: int) -> List[Payment]:
    """
    Синхронно получает список платежей с Клиента.

    :param client_id: ID Клиента.
    :param db: Активная синхронная сессия базы данных.
    :return: Список объектов платежей (моделей SQLAlchemy).
    """
    stmt = select(Payment).where(Payment.client_id == client_id)
    result = db.execute(stmt)
    return result.scalars().all()


def get_accruals_by_client(db: Session, client_id: int) -> List[Accrual]:
    """
        Синхронно получает список начислений Клиента.

        :param client_id: ID Клиента.
        :param db: Активная синхронная сессия базы данных.
        :return: Список объектов платежей (моделей SQLAlchemy).
        """
    stmt = select(Accrual).where(Accrual.client_id == client_id)
    result = db.execute(stmt)
    return result.scalars().all()


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


def create_accrual_daily(db: Session, client_id: int, count_days: int, accrual_date: datetime) -> Optional[Accrual] | None:
    """
        Синхронно добавляет новые начисление в базу данных.

        :param db: Активная синхронная сессия базы данных.
        :param client_id: ID клиента.
        :param count_days: Количество дней для расчета оплаты.
        :param accrual_date: За какой месяц рассчитано начисление
        :return: Созданный объект начисления (модель SQLAlchemy).
        """

    client = get_client_by_id(db, client_id)
    if client is None or client.is_active == 0:
        return None  # Неактивный или несуществующий клиент не списывается

    # 1. Ищем тариф, чтобы узнать цену
    tariff = get_tariff_by_name(db, client.tariff)
    if tariff is None:
        print(f"⚠️ Тариф '{client.tariff}' для клиента {client.full_name} не найден. Списание невозможно.")
        return client  # Возвращаем клиента без изменений

    charge_amount = tariff.monthly_price // 30 * count_days

    accrual = AccrualCreate(
        amount=charge_amount,
        client_id=client.id,
        accrual_date=accrual_date
    )
    accrual_db = create_accrual(db, accrual)

    return accrual_db


def create_accrual_monthly(db: Session, client_id: int, accrual_date: datetime) -> Optional[Accrual] | None:
    """
        Синхронно добавляет новые начисление в базу данных.

        :param db: Активная синхронная сессия базы данных.
        :param client_id: ID клиента.
        :param accrual_date: За какой месяц рассчитано начисление
        :return: Созданный объект начисления (модель SQLAlchemy).
        """

    client = get_client_by_id(db, client_id)
    if client is None or client.is_active == 0:
        return None  # Неактивный или несуществующий клиент не списывается

    # 1. Ищем тариф, чтобы узнать цену
    tariff = get_tariff_by_name(db, client.tariff)
    if tariff is None:
        print(f"⚠️ Тариф '{client.tariff}' для клиента {client.full_name} не найден. Списание невозможно.")
        return client  # Возвращаем клиента без изменений

    charge_amount = tariff.monthly_price

    accrual = AccrualCreate(
        amount=charge_amount,
        client_id=client.id,
        accrual_date=accrual_date
    )
    accrual_db = create_accrual(db, accrual)

    return accrual_db