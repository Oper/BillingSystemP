from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Client
from src.models.clients import ClientCreate


async def create_client(db: AsyncSession, client_data: ClientCreate) -> Client:
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

    # 3. Добавляем объект в сессию и фиксируем изменения в базе
    db.add(db_client)
    await db.commit()
    # await db.refresh(db_client) # Обновляем объект, чтобы получить ID

    return db_client