import tkinter
from tkinter import ttk, messagebox
from tkinter.constants import END

from pydantic import ValidationError

from src.models.clients import ClientUpdate
from src.db.crud import create_client, search_clients, get_clients, get_tariffs
from src.db.crud import get_client_by_id, delete_client, get_client_by_pa, update_client
from src.db.database import get_db, init_db
from src.models.clients import ClientBase
from src.models.clients import ClientCreate


class BillingSysemApp(tkinter.Tk):
    """Основной класс приложения с графическим интерфейсом."""

    def __init__(self):
        super().__init__()
        self.title("Учет Клиентов Кабельного ТВ")
        self.geometry("800x600")

        # Инициализация БД
        init_db()

        # Создание вкладок (Notebook)
        notebook = ttk.Notebook(self)
        notebook.pack(pady=10, padx=10, expand=True, fill="both")

        # Создание фреймов для вкладок
        abonents = ttk.Frame(notebook)
        tariffs = ttk.Frame(notebook)

        notebook.add(abonents, text="Абоненты")
        notebook.add(tariffs, text="Тарифы")

        # Наполнение вкладок
        self._setup_abonents_tab(abonents)

    def _setup_abonents_tab(self, frame):
        """Создает элементы для вкладки 'Абоненты'."""

        search_frame = ttk.Frame(frame)
        search_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(search_frame, text="Поиск (ФИО/Адрес):").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(search_frame, text="Найти", command=self._search_clients).pack(side="left", padx=5)
        ttk.Button(search_frame, text="Сброс", command=self._load_clients).pack(side="left", padx=5)

        # Виджет Treeview для отображения данных
        self.client_tree = ttk.Treeview(
            frame,
            columns=("Лицевой счет", "ФИО", "Адрес", "Тариф", "Баланс", "Активен"),
            show='headings'  # Скрываем первый столбец с индексами
        )
        self.client_tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Настройка заголовков столбцов
        for col in self.client_tree['columns']:
            self.client_tree.heading(col, text=col)
            self.client_tree.column(col, anchor="w", width=80)

        self.client_tree.column("Лицевой счет", width=30)
        self.client_tree.column("Баланс", width=60)
        self.client_tree.column("Активен", width=60)

        ttk.Button(frame, text="Внести оплату", command=self._add_payment).pack(side="left", padx=5)
        ttk.Button(frame, text="Приостановить").pack(side="left", padx=5)
        ttk.Button(frame, text="Возобновить").pack(side="left", padx=5)
        ttk.Separator(frame, orient="vertical", style="black.TSeparator").pack(side="left", padx=5, pady=5)
        ttk.Button(frame, text="Добавить клиента", command=self._add_client).pack(side="left", padx=5)
        ttk.Button(frame, text="Редактировать клиента", command=self._edit_client).pack(side="left", padx=5)
        ttk.Button(frame, text="Удалить клиента", command=self._delete_client).pack(side="left", padx=5)
        # Загрузка данных при старте
        self._load_clients()

    def _search_clients(self):
        """Выполняет поиск клиентов."""
        search_term = self.search_entry.get().strip()
        if not search_term:
            self._load_clients()
            return

        clients = None

        for db in get_db():
            clients = search_clients(db, search_term)
            break

        self._display_clients(clients)

    def _load_clients(self):
        """Загружает и отображает список всех клиентов (или сброс поиска)."""
        # 1. Очистка Treeview
        for item in self.client_tree.get_children():
            self.client_tree.delete(item)

        clients = None

        # 2. Получение данных
        for db in get_db():
            clients = get_clients(db)
            break

        # 3. Отображение
        self._display_clients(clients)

    def _display_clients(self, clients):
        """Отображает список объектов клиентов в Treeview."""
        # Очистка Treeview
        for item in self.client_tree.get_children():
            self.client_tree.delete(item)

        for client in clients:
            # Преобразуем объект SQLAlchemy в удобный кортеж
            is_active_status = "Да" if client.is_active == 1 else "Нет"

            self.client_tree.insert("", "end", values=(
                client.personal_account,
                client.full_name,
                client.address,
                client.tariff,
                f"{client.balance:.2f}",  # Форматируем баланс
                is_active_status
            ))

    def _setup_tariff_tab(self, frame):

        # Виджет Treeview для отображения данных
        self.tariffs_tree = ttk.Treeview(
            frame,
            columns=("Название", "Стоимость"),
            show='headings'  # Скрываем первый столбец с индексами
        )
        self.tariffs_tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Настройка заголовков столбцов
        for col in self.tariffs_tree['columns']:
            self.tariffs_tree.heading(col, text=col)
            self.tariffs_tree.column(col, anchor="w", width=80)

        # Загрузка данных при старте
        self._load_tariffs()

    def _load_tariffs(self):
        """Загружает и отображает список всех Тарифов."""
        # 1. Очистка Treeview
        for item in self.tariffs_tree.get_children():
            self.tariffs_tree.delete(item)
        tariffs = None
        # 2. Получение данных
        for db in get_db():
            tariffs = get_tariffs(db)
            break

        # 3. Отображение
        self._display_clients(tariffs)

    def _delete_client(self):
        """Обрабатывает нажатие кнопки 'Удалить клиента'."""
        select_client = self.client_tree.item(self.client_tree.focus()).get('values')
        if not select_client:
            messagebox.showerror(
                "Внимание!",
                "Необходимо выбрать абонента!"
            )
        else:
            try:
                for db in get_db():
                    client = get_client_by_id(db, select_client[0])
                    delete_client(db, select_client[0])
                    messagebox.showinfo(
                        "Успех",
                        f"Клиент {client.full_name} (ID: {client.id}) успешно удален!"
                    )
                    break
            except Exception as e:
                messagebox.showerror("Ошибка удаления", f"Не удалось удалить клиента:\n{e}")

            self._search_clients()

    def _edit_client(self):
        """Обрабатывает нажатие кнопки 'Редактировать клиента'."""
        client_id = None
        select_client = self.client_tree.item(self.client_tree.focus()).get('values')
        if not select_client:
            messagebox.showerror(
                "Внимание!",
                "Необходимо выбрать абонента!"
            )
        else:
            client_id = select_client[0]

        try:
            if client_id:
                for db in get_db():
                    client = get_client_by_id(db, client_id)
                    current_client = ClientBase(
                        personal_account=int(client.personal_account),
                        full_name=str(client.full_name),
                        address=str(client.address),
                        phone_number=str(client.phone_number),
                        tariff=str(client.tariff),
                        balance=float(client.balance),
                    )
                    new_window_edit_client = WindowAddClient(self)
                    new_window_edit_client.set_data_client(current_client)
                    break


        except Exception as e:
            print(e)

    def _delete_tariff(self):
        """Обрабатывает нажатие кнопки 'Удалить тариф'."""
        pass

    def _add_client(self):
        """Создание нового окна для добавления клиента."""

        add_window = WindowAddClient(self)

    def _add_payment(self):
        """Создание окна для внесения оплаты."""
        # TODO
        client_id = None
        select_client = self.client_tree.item(self.client_tree.focus()).get('values')
        if not select_client:
            messagebox.showerror(
                "Внимание!",
                "Необходимо выбрать абонента!"
            )
        else:
            client_id = select_client[0]
            try:
                if client_id:
                    for db in get_db():
                        client = get_client_by_id(db, client_id)
                        current_client = ClientBase(
                            personal_account=int(client.personal_account),
                            full_name=str(client.full_name),
                            address=str(client.address),
                            phone_number=str(client.phone_number),
                            tariff=str(client.tariff),
                            balance=float(client.balance),
                        )
                        new_window_edit_client = WindowAddPayment(self)
                        new_window_edit_client.set_data_client(current_client)
                        break


            except Exception as e:
                print(e)
        window_add_payment = WindowAddPayment(self)


class WindowAddClient(tkinter.Toplevel):
    """Класс для вызова окна добавления клиента."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title('Добавить клиента')
        self.geometry('400x300')
        self.resizable(False, False)

        # Заголовки и поля ввода
        ttk.Label(self, text="Лицевой счет:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.personal_account_entry = ttk.Entry(self, width=40)
        self.personal_account_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self, text="ФИО:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.full_name_entry = ttk.Entry(self, width=40)
        self.full_name_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self, text="Адрес:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.address_entry = ttk.Entry(self, width=40)
        self.address_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self, text="Телефон:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.phone_entry = ttk.Entry(self, width=40)
        self.phone_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(self, text="Тариф:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.tariff_entry = ttk.Combobox(self, width=40)
        self.tariff_entry.grid(row=4, column=1, padx=5, pady=5)

        ttk.Label(self, text="Баланс:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.balance_entry = ttk.Entry(self, width=40)
        self.balance_entry.grid(row=5, column=1, padx=5, pady=5)

        # Кнопка добавления
        ttk.Button(self, text="Отправить", command=self._send_data_client).grid(
            row=6, column=0, columnspan=2, pady=10
        )
        ttk.Button(self, text="Очистить поля", command=self._clear_add_fields).grid(
            row=7, column=0, columnspan=2, pady=10
        )

        self.transient(parent)
        self.grab_set()

    def _add_client(self, data):
        """Обрабатывает нажатие кнопки "Добавить Клиента"."""
        try:

            # 2. Вызов синхронной CRUD-функции
            for db in get_db():
                new_client = create_client(db, data)
                messagebox.showinfo(
                    "Успех",
                    f"Клиент {new_client.full_name} (ID: {new_client.id}) успешно добавлен!"
                )
                break

            self.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка добавления", f"Не удалось добавить клиента:\n{e}")

    def _update_client(self, client_id: int, client: ClientUpdate):
        """Редактирование Клиента в дополнительном окне.

        :param client_id: ID клиента в базе данных.
        :param client: Данные выбранного Клиента в главном окне.
        """
        try:

            # 2. Вызов синхронной CRUD-функции
            for db in get_db():
                current_client = update_client(db, client_id, client)
                messagebox.showinfo(
                    "Успех",
                    f"Клиент {current_client.full_name} (ID: {current_client.id}) успешно изменен!"
                )
                break

            self.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка изменения", f"Не удалось изменить клиента:\n{e}")

    def _clear_add_fields(self):
        """Очищает поля ввода после добавления."""

        self.personal_account_entry.delete(0, END)
        self.full_name_entry.delete(0, END)
        self.address_entry.delete(0, END)
        self.phone_entry.delete(0, END)
        self.tariff_entry.delete(0, END)
        self.balance_entry.delete(0, END)
        self.balance_entry.delete(0, END)

    def set_data_client(self, client: ClientBase):
        """Заполняем данные клиента с базы для редактирования"""
        self.personal_account_entry.insert(0, client.personal_account)
        self.full_name_entry.insert(0, client.full_name)
        self.address_entry.insert(0, client.address)
        self.phone_entry.insert(0, client.phone_number)
        self.tariff_entry.insert(0, client.tariff)
        self.balance_entry.insert(0, client.balance)

    def _send_data_client(self):
        """Общий метод для реализации добавления клиента в базу
         или обновления клиента в базе."""
        # 1. Сбор данных
        window_data = {
            "personal_account": self.personal_account_entry.get(),
            "full_name": self.full_name_entry.get(),
            "address": self.address_entry.get(),
            "phone_number": self.phone_entry.get(),
            "tariff": self.tariff_entry.get(),
            "balance": self.balance_entry.get(),
        }

        if window_data.values():
            try:
                data = ClientCreate(**window_data)

                for db in get_db():
                    # Проверка клиента в базе
                    client = get_client_by_pa(db, int(data.personal_account))
                    if not client:
                        self._add_client(data)
                    else:
                        current_client = ClientUpdate(
                            full_name=self.full_name_entry.get(),
                            address=self.address_entry.get(),
                            phone_number=self.phone_entry.get(),
                            tariff=self.tariff_entry.get(),
                        )
                        self._update_client(int(client.id), current_client)

            except (Exception, ValidationError) as e:
                messagebox.showerror(
                    "Ошибка",
                    f"Возникла ошибка!\nПодробности: {e}"
                )
        else:
            messagebox.showerror(
                "Ошибка!",
                "Заполните все поля!"
            )


class WindowAddPayment(tkinter.Toplevel):
    """Класс для вызова окна внесения оплаты."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Внести оплату")
        self.geometry("330x250")
        self.resizable(False, False)

        # Создаем фрейм (рамку) для лучшего размещения элементов (Padding)
        main_frame = ttk.Frame(self, padding="20 20 20 20")
        main_frame.pack(fill='both', expand=True)

        # Использование сетки (Grid) для расположения элементов

        # --- 1. Сумма платежа ---
        ttk.Label(main_frame, text="Сумма (RUB):").grid(column=0, row=0, sticky=tkinter.W, pady=5)
        amount_entry = ttk.Entry(main_frame, width=30)
        # 'W' (west) означает выравнивание по левому краю
        amount_entry.grid(column=1, row=0, padx=10, pady=5, sticky=tkinter.E)
        amount_entry.insert(0, "600.00")  # Значение по умолчанию


        ttk.Label(main_frame, text="Номер карты:").grid(column=0, row=1, sticky=tkinter.W, pady=5)
        card_entry = ttk.Entry(main_frame, width=30)
        card_entry.grid(column=1, row=1, padx=10, pady=5, sticky=tkinter.E)

        # --- 4. Кнопка "Оплатить" ---
        payment_button = ttk.Button(main_frame, text="Оплатить", command=self._process_payment)
        # Размещаем кнопку на всю ширину под полями
        payment_button.grid(column=0, row=3, columnspan=2, pady=20, sticky=tkinter.W + tkinter.E)

        self.transient(parent)
        self.grab_set()

    def _process_payment(self):
        """Обработка нажатия кнопки добавления платежа."""
        pass

    def set_data_client(self, current_client):
        pass


# --- Запуск приложения ---
if __name__ == "__main__":
    app = BillingSysemApp()
    app.mainloop()
