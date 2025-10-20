import asyncio
from db.database import get_db
from db.crud import create_client
from models.clients import ClientCreate

# Асинхронная функция, которая запускает всю логику
async def main():
    # 1. Инициализация базы данных (создание таблиц, если их нет)
    # await init_db()

    # 2. Создание данных нового клиента с помощью Pydantic
    new_client_data = ClientCreate(
        full_name="Иванов Иван Иванович",
        address="г. Москва, ул. Примерная, д. 5, кв. 10",
        phone_number="+79031234567",
        tariff="Базовый HD",
        balance=150.0
    )

    print("\n--- Попытка создания клиента ---")

    # 3. Получаем асинхронную сессию и используем ее
    # Используем 'async for' для 'get_db' (как асинхронный контекстный менеджер)
    async for db_session in get_db():
        # Вызываем нашу функцию CRUD для создания
        created_client = await create_client(db=db_session, client_data=new_client_data)

        # 4. Выводим результат
        print(f"✅ Клиент успешно добавлен! ID: {created_client.id}")
        print(f"   ФИО: {created_client.full_name}")
        print(f"   Баланс: {created_client.balance} руб.")
        print(f"   Дата подключения: {created_client.connection_date.strftime('%Y-%m-%d %H:%M')}")


# Запуск основной асинхронной функции
if __name__ == "__main__":
    asyncio.run(main())