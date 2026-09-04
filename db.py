"""Работа с базой данных SQLite.

Модуль отвечает за сохранение и загрузку данных между запусками
приложения, а также за импорт и экспорт в форматы CSV и JSON.
"""

from __future__ import annotations

import csv
import json
import os
import sqlite3
from typing import List, Optional

from models import Customer, Order, OrderItem, Product


class Database:
    """Управление базой данных SQLite.

    Parameters
    ----------
    db_path : str, optional
        Путь к файлу базы данных. По умолчанию "shop.db" в текущей директории.
    """

    def __init__(self, db_path: str = "shop.db") -> None:
        self._db_path = db_path
        self._init_schema()

    def _init_schema(self) -> None:
        """Создать таблицы базы данных, если они отсутствуют."""
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    category TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS customers (
                    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    phone TEXT NOT NULL,
                    city TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    order_date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
                );

                CREATE TABLE IF NOT EXISTS order_items (
                    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders (order_id),
                    FOREIGN KEY (product_id) REFERENCES products (product_id)
                );
                """
            )

    def _connect(self) -> sqlite3.Connection:
        """Установить соединение с базой данных.

        Returns
        -------
        sqlite3.Connection
            Соединение с включёнными внешними ключами.
        """
        conn = sqlite3.connect(self._db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # --- Товары ---

    def add_product(self, product: Product) -> int:
        """Добавить товар в базу.

        Parameters
        ----------
        product : Product
            Товар для добавления.

        Returns
        -------
        int
            Идентификатор добавленного товара.
        """
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO products (name, price, category) VALUES (?, ?, ?)",
                (product.name, product.price, product.category),
            )
            product.product_id = cur.lastrowid
            return cur.lastrowid

    def update_product(self, product: Product) -> None:
        """Обновить данные товара в базе.

        Parameters
        ----------
        product : Product
            Товар с обновлёнными данными.
        """
        with self._connect() as conn:
            conn.execute(
                "UPDATE products SET name = ?, price = ?, category = ? WHERE product_id = ?",
                (product.name, product.price, product.category, product.product_id),
            )

    def delete_product(self, product_id: int) -> None:
        """Удалить товар по идентификатору.

        Parameters
        ----------
        product_id : int
            Идентификатор товара.
        """
        with self._connect() as conn:
            conn.execute("DELETE FROM products WHERE product_id = ?", (product_id,))

    def get_product(self, product_id: int) -> Optional[Product]:
        """Получить товар по идентификатору.

        Parameters
        ----------
        product_id : int
            Идентификатор товара.

        Returns
        -------
        Product | None
            Товар или None, если товар не найден.
        """
        with self._connect() as conn:
            row = conn.execute(
                "SELECT product_id, name, price, category FROM products WHERE product_id = ?",
                (product_id,),
            ).fetchone()
        if row is None:
            return None
        return Product(row[1], row[2], row[3], product_id=row[0])

    def get_all_products(self) -> List[Product]:
        """Получить список всех товаров.

        Returns
        -------
        list[Product]
            Список товаров.
        """
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT product_id, name, price, category FROM products ORDER BY name"
            ).fetchall()
        return [Product(r[1], r[2], r[3], product_id=r[0]) for r in rows]

    # --- Клиенты ---

    def add_customer(self, customer: Customer) -> int:
        """Добавить клиента в базу.

        Parameters
        ----------
        customer : Customer
            Клиент для добавления.

        Returns
        -------
        int
            Идентификатор добавленного клиента.
        """
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO customers (name, email, phone, city) VALUES (?, ?, ?, ?)",
                (customer.name, customer.email, customer.phone, customer.city),
            )
            customer.customer_id = cur.lastrowid
            return cur.lastrowid

    def update_customer(self, customer: Customer) -> None:
        """Обновить данные клиента в базе.

        Parameters
        ----------
        customer : Customer
            Клиент с обновлёнными данными.
        """
        with self._connect() as conn:
            conn.execute(
                "UPDATE customers SET name = ?, email = ?, phone = ?, city = ? "
                "WHERE customer_id = ?",
                (
                    customer.name,
                    customer.email,
                    customer.phone,
                    customer.city,
                    customer.customer_id,
                ),
            )

    def delete_customer(self, customer_id: int) -> None:
        """Удалить клиента по идентификатору.

        Parameters
        ----------
        customer_id : int
            Идентификатор клиента.
        """
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM customers WHERE customer_id = ?", (customer_id,)
            )

    def get_customer(self, customer_id: int) -> Optional[Customer]:
        """Получить клиента по идентификатору.

        Parameters
        ----------
        customer_id : int
            Идентификатор клиента.

        Returns
        -------
        Customer | None
            Клиент или None, если клиент не найден.
        """
        with self._connect() as conn:
            row = conn.execute(
                "SELECT customer_id, name, email, phone, city "
                "FROM customers WHERE customer_id = ?",
                (customer_id,),
            ).fetchone()
        if row is None:
            return None
        return Customer(row[1], row[2], row[3], row[4], customer_id=row[0])

    def get_all_customers(self) -> List[Customer]:
        """Получить список всех клиентов.

        Returns
        -------
        list[Customer]
            Список клиентов.
        """
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT customer_id, name, email, phone, city "
                "FROM customers ORDER BY name"
            ).fetchall()
        return [Customer(r[1], r[2], r[3], r[4], customer_id=r[0]) for r in rows]

    def search_customers(self, query: str) -> List[Customer]:
        """Поиск клиентов по имени, email, телефону или городу.

        Parameters
        ----------
        query : str
            Строка поиска.

        Returns
        -------
        list[Customer]
            Список найденных клиентов.
        """
        like = f"%{query}%"
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT customer_id, name, email, phone, city FROM customers "
                "WHERE name LIKE ? OR email LIKE ? OR phone LIKE ? OR city LIKE ? "
                "ORDER BY name",
                (like, like, like, like),
            ).fetchall()
        return [Customer(r[1], r[2], r[3], r[4], customer_id=r[0]) for r in rows]

    # --- Заказы ---

    def add_order(self, order: Order) -> int:
        """Добавить заказ в базу.

        Parameters
        ----------
        order : Order
            Заказ для добавления.

        Returns
        -------
        int
            Идентификатор добавленного заказа.
        """
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO orders (customer_id, order_date, status) VALUES (?, ?, ?)",
                (order.customer.customer_id, order.order_date, order.status),
            )
            order_id = cur.lastrowid
            for item in order.items:
                conn.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity) "
                    "VALUES (?, ?, ?)",
                    (order_id, item.product.product_id, item.quantity),
                )
            order.order_id = order_id
            return order_id

    def delete_order(self, order_id: int) -> None:
        """Удалить заказ по идентификатору.

        Parameters
        ----------
        order_id : int
            Идентификатор заказа.
        """
        with self._connect() as conn:
            conn.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
            conn.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))

    def get_all_orders(self) -> List[Order]:
        """Получить список всех заказов.

        Returns
        -------
        list[Order]
            Список заказов.
        """
        products = {p.product_id: p for p in self.get_all_products()}
        customers = {c.customer_id: c for c in self.get_all_customers()}
        with self._connect() as conn:
            order_rows = conn.execute(
                "SELECT order_id, customer_id, order_date, status FROM orders"
            ).fetchall()
            item_rows = conn.execute(
                "SELECT order_id, product_id, quantity FROM order_items"
            ).fetchall()

        items_by_order: dict = {}
        for order_id, product_id, quantity in item_rows:
            items_by_order.setdefault(order_id, []).append((product_id, quantity))

        orders = []
        for order_id, customer_id, order_date, status in order_rows:
            customer = customers.get(customer_id)
            if customer is None:
                continue
            order = Order(
                customer=customer,
                order_date=order_date,
                status=status,
                order_id=order_id,
            )
            for product_id, quantity in items_by_order.get(order_id, []):
                product = products.get(product_id)
                if product is not None:
                    order.add_item(product, quantity)
            orders.append(order)
        return orders

    # --- Импорт / экспорт ---

    def export_json(self, path: str) -> None:
        """Экспортировать все данные в файл JSON.

        Parameters
        ----------
        path : str
            Путь к файлу JSON.
        """
        data = {
            "products": [p.to_dict() for p in self.get_all_products()],
            "customers": [c.to_dict() for c in self.get_all_customers()],
            "orders": [o.to_dict() for o in self.get_all_orders()],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def import_json(self, path: str) -> None:
        """Импортировать данные из файла JSON.

        Parameters
        ----------
        path : str
            Путь к файлу JSON.
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for p_data in data.get("products", []):
            self.add_product(Product.from_dict(p_data))
        for c_data in data.get("customers", []):
            self.add_customer(Customer.from_dict(c_data))
        products = self.get_all_products()
        customers = self.get_all_customers()
        customer_map = {c.name: c for c in customers}
        for o_data in data.get("orders", []):
            customer = customer_map.get(o_data.get("customer_name"))
            if customer is None:
                continue
            order = Order.from_dict(o_data, customer, products)
            self.add_order(order)

    def export_orders_csv(self, path: str) -> None:
        """Экспортировать заказы в файл CSV.

        Parameters
        ----------
        path : str
            Путь к файлу CSV.
        """
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(
                ["order_id", "date", "customer_name", "customer_city", "status", "total"]
            )
            for order in self.get_all_orders():
                writer.writerow(
                    [
                        order.order_id,
                        order.order_date,
                        order.customer.name,
                        order.customer.city,
                        order.status,
                        f"{order.total():.2f}",
                    ]
                )

    def export_customers_csv(self, path: str) -> None:
        """Экспортировать клиентов в файл CSV.

        Parameters
        ----------
        path : str
            Путь к файлу CSV.
        """
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["customer_id", "name", "email", "phone", "city"])
            for customer in self.get_all_customers():
                writer.writerow(
                    [
                        customer.customer_id,
                        customer.name,
                        customer.email,
                        customer.phone,
                        customer.city,
                    ]
                )

    def export_products_csv(self, path: str) -> None:
        """Экспортировать товары в файл CSV.

        Parameters
        ----------
        path : str
            Путь к файлу CSV.
        """
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["product_id", "name", "price", "category"])
            for product in self.get_all_products():
                writer.writerow(
                    [product.product_id, product.name, product.price, product.category]
                )

    def import_csv(self, path: str) -> str:
        """Импортировать данные из CSV-файла.

        Формат определяется по заголовку первой строки.

        Parameters
        ----------
        path : str
            Путь к файлу CSV.

        Returns
        -------
        str
            Сообщение о результате импорта.
        """
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            rows = list(reader)
        if not rows:
            return "Файл CSV пуст"
        first = rows[0]
        headers = set(first.keys())
        count = 0
        if "product_id" in headers and "category" in headers:
            for row in rows:
                self.add_product(
                    Product(row["name"], float(row["price"]), row["category"])
                )
                count += 1
            return f"Импортировано товаров: {count}"
        if "customer_id" in headers and "city" in headers:
            for row in rows:
                self.add_customer(
                    Customer(row["name"], row["email"], row["phone"], row["city"])
                )
                count += 1
            return f"Импортировано клиентов: {count}"
        return f"Неподдерживаемый формат CSV: {headers}"
