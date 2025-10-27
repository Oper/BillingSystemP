from typing import List, Optional

from sqlalchemy import select, or_, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.tariffs import TariffCreate
from src.db.models import Client, Tariff
from src.models.clients import ClientCreate, ClientUpdate


def create_client(db: AsyncSession, client_data: ClientCreate) -> Client:
    """
    Асинхронно добавляет нового клиента в базу данных.

    :param db: Активная асинхронная сессия базы данных.
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
        # await db.refresh(db_client) # Обновляем объект, чтобы получить ID
    except Exception as e:
        db.rollback()
    return db_client

def delete_client(db: AsyncSession, client_id: int) -> bool:
    """
        Асинхронно удаляет клиента в базе данных.

        :param db: Активная асинхронная сессия базы данных.
        :param client_id: Идентификатор клиента.
        :return: True, если клиент был успешно удален, False в противном случае.
        """
    # 1. Формируем запрос на удаление
    # DELETE FROM clients WHERE id = :client_id
    stmt = delete(Client).where(Client.id == client_id)

    # 2. Выполняем запрос
    result = db.execute(stmt)

    # 3. Фиксируем изменения
    db.commit()

    # rowcount > 0 означает, что была удалена хотя бы одна запись
    return result.rowcount > 0


def get_client_by_id(db: AsyncSession, client_id: int) -> Optional[Client]:
    """
    Асинхронно получает одного клиента по его уникальному ID.

    :param db: Активная асинхронная сессия базы данных.
    :param client_id: Уникальный ID клиента.
    :return: Объект клиента или None, если клиент не найден.
    """
    # Формируем запрос: SELECT * FROM clients WHERE id = :client_id
    stmt = select(Client).where(Client.id == client_id)

    # Выполняем запрос и возвращаем первый найденный объект (или None)
    result = db.execute(stmt)
    return result.scalars().first()


def update_client(db: AsyncSession, client_id: int, client_data: ClientUpdate) -> Optional[Client]:
    """
    Асинхронно обновляет данные существующего клиента.

    :param db: Активная асинхронная сессия базы данных.
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


def get_clients(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Client]:
    """
    Асинхронно получает список клиентов с возможностью пагинации.

    :param db: Активная асинхронная сессия базы данных.
    :param skip: Количество записей, которое нужно пропустить (смещение).
    :param limit: Максимальное количество записей для возврата.
    :return: Список объектов клиентов (моделей SQLAlchemy).
    """
    # 1. Формируем асинхронный запрос: SELECT * FROM clients
    stmt = select(Client).offset(skip).limit(limit)

    # 2. Выполняем запрос
    result = db.execute(stmt)

    # 3. Получаем все результаты (scalar_all)
    # .scalars() возвращает объекты модели Client, а не кортежи
    return result.scalars().all()


def search_clients(db: AsyncSession, search_term: str) -> List[Client]:
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

def create_tariff(db: AsyncSession, tariff_data: TariffCreate) -> Tariff:
    """Добавляет новый тариф."""
    db_tariff = Tariff(**tariff_data.model_dump())
    db.add(db_tariff)
    db.commit()
    return db_tariff

def get_tariff_by_name(db: AsyncSession, name: str) -> Optional[Tariff]:
    """Находит тариф по имени."""
    stmt = select(Tariff).where(func.lower(Tariff.name) == func.lower(name))
    result = db.execute(stmt)
    return result.scalars().first()

def get_tariffs(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Tariff]:
    """Получение списка Тарифов"""
    stmt = select(Tariff).offset(skip).limit(limit)
    result = db.execute(stmt)
    return result.scalars().all()


def apply_monthly_charge(db: AsyncSession, client_id: int) -> Optional[Client]:
    """
    Рассчитывает ежемесячную плату для клиента и вычитает ее из баланса.

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


def set_client_activity(db: AsyncSession, client_id: int, is_active: bool) -> Optional[Client]:
    """
    Приостанавливает (is_active=False) или возобновляет (is_active=True) обслуживание клиента.

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