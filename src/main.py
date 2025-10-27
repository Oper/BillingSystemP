import asyncio
from db.database import get_db
from db.crud import create_client, delete_client, get_client_by_id, get_clients
from models.clients import ClientCreate

# Асинхронная функция, которая запускает всю логику
async def main():
    COMMANDS = {
        "create_client": 'create_client',
        "delete_client": 'delete_client',
        "list_clients": 'list_clients',
        "exit": exit,
    }

    while True:
        command = input('Введите команду: ')
        if command == 'exit':
            break
        elif command == 'help':
            print(*COMMANDS, sep='\n')
        elif command == 'create_client':
            full_name = input('ФИО, например Иванов Иван Иванович ')
            address = input('Адрес, например г. Москва, ул. Примерная, д. 5, кв. 10 ')
            phone_number = input('Телефон, например +79031234567 ')
            tariff = input('Тариф, например Базовый ')
            balance = float(input('Баланс, например 150.0 '))

            print("\n--- Попытка создания клиента ---")
            new_client_data = ClientCreate(
                full_name=full_name,
                address=address,
                phone_number=phone_number,
                tariff=tariff,
                balance=balance
            )
            async for db_session in get_db():
                created_client = await create_client(db=db_session, client_data=new_client_data)
                print(f"✅ Клиент успешно добавлен! ID: {created_client.id}")
                print(f"   ФИО: {created_client.full_name}")
                print(f"   Баланс: {created_client.balance} руб.")
                print(f"   Дата подключения: {created_client.connection_date.strftime('%Y-%m-%d %H:%M')}")

        elif command == 'delete_client':
            client_id = int(input('Введите ID клиента: '))
            async for db_session in get_db():
                client = await get_client_by_id(db=db_session, client_id=client_id)
                is_delete_client = await delete_client(db=db_session, client_id=client_id)
                if is_delete_client:
                    print(f"✅ Клиент успешно удален! ID: {client.id}")
                    print(f"   ФИО: {client.full_name}")
        elif command == 'list_clients':
            async for db_session in get_db():
                clients = await get_clients(db=db_session)
                if clients:
                    for client in clients:
                        print(f"Клиент {client.full_name} Адрес: {client.address}, ID: {client.id}")

    # 1. Инициализация базы данных (создание таблиц, если их нет)
    # await init_db()

    # 2. Создание данных нового клиента с помощью Pydantic
    # new_client_data = ClientCreate(
    #     full_name="Иванов Иван Иванович",
    #     address="г. Москва, ул. Примерная, д. 5, кв. 10",
    #     phone_number="+79031234567",
    #     tariff="Базовый HD",
    #     balance=150.0
    # )
    #
    # print("\n--- Попытка создания клиента ---")
    #
    # # 3. Получаем асинхронную сессию и используем ее
    # # Используем 'async for' для 'get_db' (как асинхронный контекстный менеджер)
    # async for db_session in get_db():
    #     # Вызываем нашу функцию CRUD для создания
    #     created_client = await create_client(db=db_session, client_data=new_client_data)
    #
    #     # 4. Выводим результат
    #     print(f"✅ Клиент успешно добавлен! ID: {created_client.id}")
    #     print(f"   ФИО: {created_client.full_name}")
    #     print(f"   Баланс: {created_client.balance} руб.")
    #     print(f"   Дата подключения: {created_client.connection_date.strftime('%Y-%m-%d %H:%M')}")
    # async for db_session in get_db():
    #     is_delete_client = await delete_client(db=db_session, client_id=1)
    #
    #     print(f'Client delete - {is_delete_client}')


# Запуск основной асинхронной функции
if __name__ == "__main__":
    asyncio.run(main())