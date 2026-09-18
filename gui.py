"""Графический интерфейс приложения на основе tkinter.

Обеспечивает регистрацию клиентов, добавление заказов, товаров,
поиск, фильтрацию, сортировку, анализ данных и экспорт в CSV.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import analysis
import charts
from db import Database
from models import Customer, Order, Product


class ShopApp:
    """Главный класс графического интерфейса.

    Parameters
    ----------
    root : tk.Tk
        Корневое окно tkinter.
    """

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Система учёта заказов")
        self.root.geometry("1100x700")
        self.db = Database("shop.xlsx")

        self._build_menu()
        self._build_tabs()
        self.refresh_all()

    # ------------------------------------------------------------------ UI

    def _build_menu(self) -> None:
        """Создать главное меню приложения."""
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Экспорт заказов в CSV", command=self.export_orders_csv)
        file_menu.add_command(label="Экспорт клиентов в CSV", command=self.export_customers_csv)
        file_menu.add_command(label="Экспорт товаров в CSV", command=self.export_products_csv)
        file_menu.add_command(label="Импорт из CSV", command=self.import_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)

        analysis_menu = tk.Menu(menubar, tearoff=0)
        analysis_menu.add_command(label="Топ 5 клиентов", command=self.show_top_customers)
        analysis_menu.add_command(
            label="Динамика заказов", command=self.show_orders_dynamics
        )
        analysis_menu.add_command(label="Топ товаров", command=self.show_top_products)
        analysis_menu.add_command(
            label="Выручка по категориям", command=self.show_sales_by_category
        )
        analysis_menu.add_command(
            label="Граф связей клиентов", command=self.show_customer_graph
        )
        menubar.add_cascade(label="Анализ", menu=analysis_menu)

        self.root.config(menu=menubar)

    def _build_tabs(self) -> None:
        """Создать вкладки интерфейса."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        self._build_customers_tab()
        self._build_products_tab()
        self._build_orders_tab()
        self._build_analysis_tab()

    # --- Вкладка клиентов ---

    def _build_customers_tab(self) -> None:
        """Создать вкладку управления клиентами."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Клиенты")

        form = ttk.LabelFrame(tab, text="Регистрация клиента")
        form.pack(fill="x", padx=10, pady=5)

        ttk.Label(form, text="Имя:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.cust_name = ttk.Entry(form, width=30)
        self.cust_name.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(form, text="Email:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.cust_email = ttk.Entry(form, width=30)
        self.cust_email.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(form, text="Телефон:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.cust_phone = ttk.Entry(form, width=30)
        self.cust_phone.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(form, text="Город:").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.cust_city = ttk.Entry(form, width=30)
        self.cust_city.grid(row=1, column=3, padx=5, pady=2)

        ttk.Button(form, text="Добавить клиента", command=self.add_customer).grid(
            row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w"
        )
        ttk.Button(form, text="Обновить клиента", command=self.update_customer).grid(
            row=2, column=2, columnspan=2, padx=5, pady=5, sticky="w"
        )

        search_frame = ttk.Frame(tab)
        search_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(search_frame, text="Поиск:").pack(side="left")
        self.cust_search = ttk.Entry(search_frame, width=40)
        self.cust_search.pack(side="left", padx=5)
        self.cust_search.bind("<KeyRelease>", lambda e: self.refresh_customers())
        ttk.Button(search_frame, text="Удалить", command=self.delete_customer).pack(
            side="right"
        )

        self.customer_tree = self._build_tree(
            tab, ("ID", "Имя", "Email", "Телефон", "Город"), widths=(50, 150, 200, 150, 120)
        )

    # --- Вкладка товаров ---

    def _build_products_tab(self) -> None:
        """Создать вкладку управления товарами."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Товары")

        form = ttk.LabelFrame(tab, text="Добавление товара")
        form.pack(fill="x", padx=10, pady=5)

        ttk.Label(form, text="Название:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.prod_name = ttk.Entry(form, width=30)
        self.prod_name.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(form, text="Цена:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.prod_price = ttk.Entry(form, width=15)
        self.prod_price.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(form, text="Категория:").grid(row=0, column=4, sticky="w", padx=5, pady=2)
        self.prod_category = ttk.Entry(form, width=20)
        self.prod_category.grid(row=0, column=5, padx=5, pady=2)

        ttk.Button(form, text="Добавить товар", command=self.add_product).grid(
            row=1, column=0, columnspan=3, padx=5, pady=5, sticky="w"
        )
        ttk.Button(form, text="Обновить товар", command=self.update_product).grid(
            row=1, column=3, columnspan=3, padx=5, pady=5, sticky="w"
        )

        self.product_tree = self._build_tree(
            tab, ("ID", "Название", "Цена", "Категория"), widths=(50, 200, 100, 150)
        )

    # --- Вкладка заказов ---

    def _build_orders_tab(self) -> None:
        """Создать вкладку управления заказами."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Заказы")

        form = ttk.LabelFrame(tab, text="Создание заказа")
        form.pack(fill="x", padx=10, pady=5)

        self.customers = self.db.get_all_customers()
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(
            form,
            textvariable=self.customer_var,
            values=[f"{c.customer_id}: {c.name}" for c in self.customers],
            width=40,
            state="readonly",
        )
        self.customer_combo.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(form, text="Клиент:").grid(row=0, column=0, sticky="w", padx=5, pady=2)

        self.status_var = tk.StringVar(value="новый")
        ttk.Label(form, text="Статус:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.status_combo = ttk.Combobox(
            form,
            textvariable=self.status_var,
            values=["новый", "в обработке", "отправлен", "доставлен", "отменён"],
            width=15,
            state="readonly",
        )
        self.status_combo.grid(row=0, column=3, padx=5, pady=2)

        ttk.Button(form, text="Создать заказ", command=self.create_order).grid(
            row=0, column=4, padx=5, pady=2
        )

        items_frame = ttk.LabelFrame(tab, text="Товары в заказе")
        items_frame.pack(fill="x", padx=10, pady=5)

        self.products = self.db.get_all_products()
        self.product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(
            items_frame,
            textvariable=self.product_var,
            values=[f"{p.product_id}: {p.name} ({p.price} руб.)" for p in self.products],
            width=50,
            state="readonly",
        )
        self.product_combo.grid(row=0, column=0, padx=5, pady=5)

        self.quantity_entry = ttk.Entry(items_frame, width=8)
        self.quantity_entry.insert(0, "1")
        self.quantity_entry.grid(row=0, column=1, padx=5, pady=5)

        self.order_items_list = tk.Listbox(items_frame, height=6)
        self.order_items_list.grid(row=1, column=0, columnspan=4, sticky="we", padx=5, pady=5)

        self._pending_items = []

        ttk.Button(items_frame, text="Добавить в заказ", command=self.add_item_to_pending).grid(
            row=0, column=2, padx=5, pady=5
        )
        ttk.Button(items_frame, text="Очистить список", command=self.clear_pending).grid(
            row=0, column=3, padx=5, pady=5
        )

        filter_frame = ttk.LabelFrame(tab, text="Фильтры и сортировка")
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Город:").grid(row=0, column=0, padx=5, pady=2)
        self.filter_city = ttk.Entry(filter_frame, width=15)
        self.filter_city.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(filter_frame, text="Статус:").grid(row=0, column=2, padx=5, pady=2)
        self.filter_status = ttk.Combobox(
            filter_frame,
            values=["", "новый", "в обработке", "отправлен", "доставлен", "отменён"],
            width=15,
            state="readonly",
        )
        self.filter_status.set("")
        self.filter_status.grid(row=0, column=3, padx=5, pady=2)

        self.filter_city.bind("<KeyRelease>", lambda e: self.refresh_orders())
        self.filter_status.bind("<<ComboboxSelected>>", lambda e: self.refresh_orders())

        ttk.Label(filter_frame, text="Сортировка:").grid(row=0, column=4, padx=5, pady=2)
        self.sort_var = tk.StringVar(value="date")
        sort_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.sort_var,
            values=["date", "total"],
            width=10,
            state="readonly",
        )
        sort_combo.grid(row=0, column=5, padx=5, pady=2)
        sort_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_orders())

        self.order_tree = self._build_tree(
            tab,
            ("ID", "Дата", "Клиент", "Город", "Статус", "Сумма"),
            widths=(50, 100, 150, 120, 120, 100),
        )

        self.order_note = ttk.Label(tab, text="", foreground="gray")
        self.order_note.pack(padx=10, pady=2)

    # --- Вкладка анализа ---

    def _build_analysis_tab(self) -> None:
        """Создать вкладку анализа данных."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Анализ")

        buttons = [
            ("Топ 5 клиентов по числу заказов", self.show_top_customers),
            ("Динамика количества заказов", self.show_orders_dynamics),
            ("Топ 5 товаров", self.show_top_products),
            ("Выручка по категориям", self.show_sales_by_category),
            ("Граф связей клиентов", self.show_customer_graph),
        ]
        for text, command in buttons:
            ttk.Button(tab, text=text, command=command).pack(
                fill="x", padx=20, pady=5
            )

        ttk.Label(tab, text="Результаты анализа:", font=("Arial", 11, "bold")).pack(
            anchor="w", padx=20, pady=(15, 5)
        )
        self.analysis_text = tk.Text(tab, height=8, wrap="word")
        self.analysis_text.pack(fill="both", expand=True, padx=20, pady=5)
        self.analysis_text.config(state="disabled")

    # ------------------------------------------------------------------ helpers

    def _build_tree(self, parent, columns: tuple, widths: tuple):
        """Создать дерево-таблицу с полосой прокрутки.

        Parameters
        ----------
        parent : tk.Widget
            Родительский виджет.
        columns : tuple
            Названия колонок.
        widths : tuple
            Ширины колонок.

        Returns
        -------
        ttk.Treeview
            Виджет таблицы.
        """
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=5)
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col, width in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="w")
        scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return tree

    def _safe(self, func, *args, **kwargs):
        """Выполнить функцию с обработкой ошибок.

        Parameters
        ----------
        func : callable
            Вызываемая функция.
        *args
            Позиционные аргументы функции.
        **kwargs
            Именованные аргументы функции.
        """
        try:
            return func(*args, **kwargs)
        except ValueError as exc:
            messagebox.showerror("Ошибка", str(exc))
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Ошибка", f"Непредвиденная ошибка: {exc}")

    def _set_analysis_text(self, lines: list) -> None:
        """Записать текстовый результат анализа в виджет.

        Parameters
        ----------
        lines : list
            Строки результата анализа.
        """
        self.analysis_text.config(state="normal")
        self.analysis_text.delete("1.0", "end")
        self.analysis_text.insert("1.0", "\n".join(lines))
        self.analysis_text.config(state="disabled")

    # ------------------------------------------------------------------ данные

    def refresh_all(self) -> None:
        """Обновить все вкладки с данными."""
        self.refresh_customers()
        self.refresh_products()
        self.refresh_orders()

    # --- Клиенты ---

    def add_customer(self) -> None:
        """Добавить клиента из формы регистрации."""
        def do():
            customer = Customer(
                self.cust_name.get(),
                self.cust_email.get(),
                self.cust_phone.get(),
                self.cust_city.get(),
            )
            self.db.add_customer(customer)
            self.cust_name.delete(0, "end")
            self.cust_email.delete(0, "end")
            self.cust_phone.delete(0, "end")
            self.cust_city.delete(0, "end")
            self.refresh_customers()
            messagebox.showinfo("Успех", f"Клиент {customer.name} добавлен")

        self._safe(do)

    def update_customer(self) -> None:
        """Обновить выбранного клиента из формы."""
        selection = self.customer_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите клиента из списка")
            return

        def do():
            item = self.customer_tree.item(selection[0])
            customer_id = int(item["values"][0])
            customer = Customer(
                self.cust_name.get() or item["values"][1],
                self.cust_email.get() or item["values"][2],
                self.cust_phone.get() or item["values"][3],
                self.cust_city.get() or item["values"][4],
                customer_id=customer_id,
            )
            self.db.update_customer(customer)
            self.refresh_customers()
            messagebox.showinfo("Успех", "Клиент обновлён")

        self._safe(do)

    def delete_customer(self) -> None:
        """Удалить выбранного клиента."""
        selection = self.customer_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите клиента из списка")
            return

        def do():
            item = self.customer_tree.item(selection[0])
            customer_id = int(item["values"][0])
            self.db.delete_customer(customer_id)
            self.refresh_all()
            messagebox.showinfo("Успех", "Клиент удалён")

        self._safe(do)

    def refresh_customers(self) -> None:
        """Обновить таблицу клиентов с учётом строки поиска."""
        for row in self.customer_tree.get_children():
            self.customer_tree.delete(row)
        query = self.cust_search.get()
        customers = self.db.search_customers(query) if query else self.db.get_all_customers()
        for c in customers:
            self.customer_tree.insert(
                "",
                "end",
                values=(c.customer_id, c.name, c.email, c.phone, c.city),
            )

    # --- Товары ---

    def add_product(self) -> None:
        """Добавить товар из формы."""
        def do():
            product = Product(
                self.prod_name.get(),
                float(self.prod_price.get()),
                self.prod_category.get(),
            )
            self.db.add_product(product)
            self.prod_name.delete(0, "end")
            self.prod_price.delete(0, "end")
            self.prod_category.delete(0, "end")
            self.refresh_products()
            messagebox.showinfo("Успех", f"Товар {product.name} добавлен")

        self._safe(do)

    def update_product(self) -> None:
        """Обновить выбранный товар."""
        selection = self.product_tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите товар из списка")
            return

        def do():
            item = self.product_tree.item(selection[0])
            product_id = int(item["values"][0])
            product = Product(
                self.prod_name.get() or item["values"][1],
                float(self.prod_price.get() or item["values"][2]),
                self.prod_category.get() or item["values"][3],
                product_id=product_id,
            )
            self.db.update_product(product)
            self.refresh_products()
            messagebox.showinfo("Успех", "Товар обновлён")

        self._safe(do)

    def refresh_products(self) -> None:
        """Обновить таблицу товаров."""
        for row in self.product_tree.get_children():
            self.product_tree.delete(row)
        self.products = self.db.get_all_products()
        self.product_combo["values"] = [
            f"{p.product_id}: {p.name} ({p.price} руб.)" for p in self.products
        ]
        for p in self.products:
            self.product_tree.insert(
                "",
                "end",
                values=(p.product_id, p.name, f"{p.price:.2f}", p.category),
            )

    # --- Заказы ---

    def add_item_to_pending(self) -> None:
        """Добавить выбранный товар в список позиций создаваемого заказа."""
        selection = self.product_var.get()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите товар")
            return
        try:
            product_id = int(selection.split(":")[0])
            quantity = int(self.quantity_entry.get())
            if quantity <= 0:
                raise ValueError("Количество должно быть больше нуля")
        except ValueError as exc:
            messagebox.showerror("Ошибка", str(exc))
            return
        product = next((p for p in self.products if p.product_id == product_id), None)
        if product is None:
            messagebox.showerror("Ошибка", "Товар не найден")
            return
        self._pending_items.append((product, quantity))
        self.order_items_list.insert(
            "end", f"{product.name} x {quantity} = {product.price * quantity:.2f} руб."
        )

    def clear_pending(self) -> None:
        """Очистить список позиций создаваемого заказа."""
        self._pending_items.clear()
        self.order_items_list.delete(0, "end")

    def create_order(self) -> None:
        """Создать заказ из выбранного клиента и накопленных позиций."""
        if not self._pending_items:
            messagebox.showwarning("Внимание", "Добавьте товары в заказ")
            return
        customer_id = self.customer_var.get()
        if not customer_id:
            messagebox.showwarning("Внимание", "Выберите клиента")
            return

        def do():
            rid = int(customer_id.split(":")[0])
            customer = self.db.get_customer(rid)
            if customer is None:
                raise ValueError("Клиент не найден")
            order = Order(customer, status=self.status_var.get())
            for product, quantity in self._pending_items:
                order.add_item(product, quantity)
            self.db.add_order(order)
            self.clear_pending()
            self.refresh_orders()
            messagebox.showinfo("Успех", f"Заказ #{order.order_id} создан")

        self._safe(do)

    def refresh_orders(self) -> None:
        """Обновить таблицу заказов с учётом фильтров и сортировки."""
        for row in self.order_tree.get_children():
            self.order_tree.delete(row)

        orders = self.db.get_all_orders()

        city = self.filter_city.get().strip().lower()
        status = self.filter_status.get()
        if city:
            orders = [o for o in orders if city in o.customer.city.lower()]
        if status:
            orders = [o for o in orders if o.status == status]

        sort_key = self.sort_var.get()
        if sort_key == "total":
            orders = sorted(orders, key=lambda o: o.total(), reverse=True)
        else:
            orders = sorted(orders, key=lambda o: o.order_date)

        for o in orders:
            self.order_tree.insert(
                "",
                "end",
                values=(
                    o.order_id,
                    o.order_date,
                    o.customer.name,
                    o.customer.city,
                    o.status,
                    f"{o.total():.2f}",
                ),
            )
        total_sum = sum(o.total() for o in orders)
        self.order_note.config(text=f"Всего заказов: {len(orders)}, сумма: {total_sum:.2f} руб.")

    # --- Анализ ---

    def show_top_customers(self) -> None:
        """Показать топ клиентов по числу заказов."""
        def do():
            orders = self.db.get_all_orders()
            data = analysis.top_customers(orders)
            lines = ["Топ клиентов по числу заказов:"]
            for i, (c, cnt) in enumerate(data, 1):
                lines.append(f"{i}. {c.name} — {cnt} заказов")
            self._set_analysis_text(lines)
            title = "Топ 5 клиентов по числу заказов"
            window, canvas = charts.create_chart_window(self.root, title)
            labels = [c.name for c, _ in data] or ["—"]
            values = [float(cnt) for _, cnt in data] or [0]
            charts.draw_bar_chart(canvas, labels, values, title)

        self._safe(do)

    def show_orders_dynamics(self) -> None:
        """Показать динамику количества заказов."""
        def do():
            orders = self.db.get_all_orders()
            data = analysis.orders_by_date(orders)
            if not data:
                raise ValueError("Нет данных для анализа")
            lines = ["Динамика заказов по датам:"]
            for row in data:
                lines.append(
                    f"{row['date']}: {row['count']} заказов, {row['sum']:.2f} руб."
                )
            self._set_analysis_text(lines)
            title = "Динамика количества заказов по датам"
            window, canvas = charts.create_chart_window(self.root, title)
            labels = [row["date"] for row in data]
            values = [float(row["count"]) for row in data]
            charts.draw_line_chart(canvas, labels, values, title)

        self._safe(do)

    def show_top_products(self) -> None:
        """Показать топ товаров по продажам."""
        def do():
            orders = self.db.get_all_orders()
            data = analysis.top_products(orders)
            lines = ["Топ товаров по количеству продаж:"]
            for i, (name, qty) in enumerate(data, 1):
                lines.append(f"{i}. {name} — {qty} шт.")
            self._set_analysis_text(lines)
            title = "Топ 5 товаров по количеству продаж"
            window, canvas = charts.create_chart_window(self.root, title)
            labels = [name for name, _ in data] or ["—"]
            values = [float(q) for _, q in data] or [0]
            charts.draw_bar_chart(canvas, labels, values, title)

        self._safe(do)

    def show_sales_by_category(self) -> None:
        """Показать выручку по категориям."""
        def do():
            orders = self.db.get_all_orders()
            data = analysis.sales_by_category(orders)
            if not data:
                raise ValueError("Нет данных для анализа")
            lines = ["Выручка по категориям:"]
            for category, revenue in data:
                lines.append(f"{category}: {revenue:.2f} руб.")
            self._set_analysis_text(lines)
            title = "Выручка по категориям товаров"
            window, canvas = charts.create_chart_window(self.root, title)
            labels = [category for category, _ in data]
            values = [float(revenue) for _, revenue in data]
            charts.draw_pie_chart(canvas, labels, values, title)

        self._safe(do)

    def show_customer_graph(self) -> None:
        """Показать граф связей клиентов."""
        def do():
            orders = self.db.get_all_orders()
            graph = analysis.build_customer_graph(orders)
            lines = [
                f"Граф связей построен: {graph.node_count()} клиентов, "
                f"{graph.edge_count()} связей."
            ]
            self._set_analysis_text(lines)
            title = "Граф связей клиентов (город / общие товары)"
            window, canvas = charts.create_chart_window(self.root, title)
            charts.draw_customer_graph(canvas, graph, title)

        self._safe(do)

    # --- Экспорт / импорт CSV ---

    def export_orders_csv(self) -> None:
        """Экспортировать заказы в CSV-файл."""
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv")]
        )
        if not path:
            return

        def do():
            self.db.export_orders_csv(path)
            messagebox.showinfo("Успех", f"Заказы экспортированы в {path}")

        self._safe(do)

    def export_customers_csv(self) -> None:
        """Экспортировать клиентов в CSV-файл."""
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv")]
        )
        if not path:
            return

        def do():
            self.db.export_customers_csv(path)
            messagebox.showinfo("Успех", f"Клиенты экспортированы в {path}")

        self._safe(do)

    def export_products_csv(self) -> None:
        """Экспортировать товары в CSV-файл."""
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV files", "*.csv")]
        )
        if not path:
            return

        def do():
            self.db.export_products_csv(path)
            messagebox.showinfo("Успех", f"Товары экспортированы в {path}")

        self._safe(do)

    def import_csv(self) -> None:
        """Импортировать данные из CSV-файла."""
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not path:
            return

        def do():
            result = self.db.import_csv(path)
            self.refresh_all()
            messagebox.showinfo("Импорт", result)

        self._safe(do)


def run() -> None:
    """Запустить графический интерфейс приложения."""
    root = tk.Tk()
    ShopApp(root)
    root.mainloop()