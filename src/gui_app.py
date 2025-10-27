import tkinter
from tkinter import ttk, messagebox
from tkinter.constants import END

from db.crud import create_client, search_clients, get_clients, get_tariffs
from db.database import get_db
from models.clients import ClientCreate


def snow_window_abonent_add():
    """Создание окна для добавления абонента"""

    new_window = WindowAddClient()


class BillingSysemApp(tkinter.Tk):
    """Основной класс приложения с графическим интерфейсом."""

    def __init__(self):
        super().__init__()
        self.title("Учет Клиентов Кабельного ТВ")
        self.geometry("800x600")

        # Инициализация БД
        # init_db()

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
            columns=("ID", "ФИО", "Адрес", "Тариф", "Баланс", "Активен"),
            show='headings'  # Скрываем первый столбец с индексами
        )
        self.client_tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Настройка заголовков столбцов
        for col in self.client_tree['columns']:
            self.client_tree.heading(col, text=col)
            self.client_tree.column(col, anchor="w", width=80)

        self.client_tree.column("ID", width=30)
        self.client_tree.column("Баланс", width=60)
        self.client_tree.column("Активен", width=60)

        ttk.Button(frame, text="Внести оплату").pack(side="left", padx=5)
        ttk.Button(frame, text="Приостановить").pack(side="left", padx=5)
        ttk.Button(frame, text="Возобновить").pack(side="left", padx=5)
        ttk.Separator(frame, orient="vertical", style="black.TSeparator").pack(side="left", padx=5, pady=5)
        ttk.Button(frame, text="Добавить клиента", command=snow_window_abonent_add).pack(side="left", padx=5)
        ttk.Button(frame, text="Редактировать клиента").pack(side="left", padx=5)
        ttk.Button(frame, text="Удалить клиента").pack(side="left", padx=5)
        # Загрузка данных при старте
        self._load_clients()


    def _clear_add_fields(self):
        """Очищает поля ввода после добавления."""
        self.full_name_entry.delete(0, END)
        self.address_entry.delete(0, END)
        self.phone_entry.delete(0, END)
        self.tariff_entry.delete(0, END)
        self.balance_entry.delete(0, END)
        self.balance_entry.insert(0, "0.0")

    def _search_clients(self):
        """Выполняет поиск клиентов."""
        search_term = self.search_entry.get().strip()
        if not search_term:
            self._load_clients()
            return

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
                client.id,
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

        # 2. Получение данных
        for db in get_db():
            tariffs = get_tariffs(db)
            break

        # 3. Отображение
        self._display_clients(tariffs)


class WindowAddClient(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.title('Добавить клиента')
        self.geometry('400x400')

        # Заголовки и поля ввода
        ttk.Label(self, text="ФИО:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.full_name_entry = ttk.Entry(self, width=40)
        self.full_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self, text="Адрес:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.address_entry = ttk.Entry(self, width=40)
        self.address_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self, text="Телефон:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.phone_entry = ttk.Entry(self, width=40)
        self.phone_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self, text="Тариф:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.tariff_entry = ttk.Combobox(self, width=40)
        self.tariff_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(self, text="Баланс:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.balance_entry = ttk.Entry(self, width=40)
        self.balance_entry.insert(0, "0.0")  # Начальное значение
        self.balance_entry.grid(row=4, column=1, padx=5, pady=5)

        # Кнопка добавления
        ttk.Button(self, text="Добавить Клиента", command=self._add_client).grid(
            row=5, column=0, columnspan=2, pady=10
        )

    def _add_client(self):
        """Обрабатывает нажатие кнопки "Добавить Клиента"."""
        try:
            # 1. Сбор данных
            data = ClientCreate(
                full_name=self.full_name_entry.get(),
                address=self.address_entry.get(),
                phone_number=self.phone_entry.get() or None,  # Если пусто, None
                tariff=self.tariff_entry.get(),
                balance=float(self.balance_entry.get())
            )
            new_client = None
            # 2. Вызов синхронной CRUD-функции
            for db in get_db():
                new_client = create_client(db, data)
                break

            messagebox.showinfo(
                "Успех",
                f"Клиент {new_client.full_name} (ID: {new_client.id}) успешно добавлен!"
            )

            # 3. Очистка полей и обновление списка
            # self._clear_add_fields()
            # self._load_clients()

        except Exception as e:
            messagebox.showerror("Ошибка добавления", f"Не удалось добавить клиента:\n{e}")

# --- Запуск приложения ---
if __name__ == "__main__":
    app = BillingSysemApp()
    app.mainloop()