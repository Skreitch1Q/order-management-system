"""Unit-тесты для модуля db.py (база данных в Excel).

Покрытие операций добавления, обновления, удаления, поиска,
а также импорта и экспорта в форматах JSON и CSV.
"""

from __future__ import annotations

import os
import tempfile
import unittest

from db import Database
from models import Customer, Order, Product


class TestDatabase(unittest.TestCase):
    """Тесты операций с базой данных на Excel."""

    def setUp(self) -> None:
        """Создание временной базы для каждого теста."""
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, "test.xlsx")
        self.db = Database(self.db_path)

    def tearDown(self) -> None:
        """Удаление временных файлов."""
        for name in os.listdir(self.tmpdir):
            os.remove(os.path.join(self.tmpdir, name))
        os.rmdir(self.tmpdir)

    def _make_products_and_customers(self) -> tuple:
        """Создать базовый набор товаров и клиентов.

        Returns
        -------
        tuple
            (список товаров, список клиентов).
        """
        p1 = Product("Ноутбук", 50000, "Электроника")
        p2 = Product("Книга", 1299, "Книги")
        self.db.add_product(p1)
        self.db.add_product(p2)
        c1 = Customer("Иван", "ivan@example.com", "+7 (999) 123-45-67", "Москва")
        c2 = Customer("Мария", "maria@example.com", "+7 (916) 555-23-41", "Москва")
        self.db.add_customer(c1)
        self.db.add_customer(c2)
        return [p1, p2], [c1, c2]

    def test_unique_ids(self) -> None:
        """Идентификаторы должны генерироваться последовательно."""
        products, customers = self._make_products_and_customers()
        self.assertEqual([p.product_id for p in products], [1, 2])
        self.assertEqual([c.customer_id for c in customers], [1, 2])

    def test_add_and_get_products(self) -> None:
        """Добавление и получение товаров."""
        self._make_products_and_customers()
        products = self.db.get_all_products()
        self.assertEqual(len(products), 2)
        names = [p.name for p in products]
        self.assertIn("Ноутбук", names)
        self.assertIn("Книга", names)

    def test_update_customer(self) -> None:
        """Обновление данных клиента."""
        products, customers = self._make_products_and_customers()
        updated = Customer(
            "Иван Петров",
            "ivan@example.com",
            "+7 (999) 123-45-67",
            "Казань",
            customer_id=customers[0].customer_id,
        )
        self.db.update_customer(updated)
        result = self.db.get_customer(customers[0].customer_id)
        self.assertEqual(result.city, "Казань")
        self.assertEqual(result.name, "Иван Петров")

    def test_delete_customer(self) -> None:
        """Удаление клиента не задевает остальных."""
        products, customers = self._make_products_and_customers()
        self.db.delete_customer(customers[0].customer_id)
        remaining = self.db.get_all_customers()
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].name, "Мария")

    def test_search_customers(self) -> None:
        """Поиск клиентов по подстроке."""
        self._make_products_and_customers()
        result = self.db.search_customers("Иван")
        self.assertEqual(len(result), 1)
        result = self.db.search_customers("Москва")
        self.assertEqual(len(result), 2)
        result = self.db.search_customers("несуществующее")
        self.assertEqual(len(result), 0)

    def test_orders_and_items(self) -> None:
        """Создание заказа с позициями и его сумма."""
        products, customers = self._make_products_and_customers()
        order = Order(customers[0], order_date="2026-06-01")
        order.add_item(products[0], 2)
        order.add_item(products[1], 1)
        self.db.add_order(order)

        orders = self.db.get_all_orders()
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].order_id, order.order_id)
        self.assertAlmostEqual(orders[0].total(), 50000 * 2 + 1299)
        self.assertEqual(len(orders[0].items), 2)

    def test_delete_order(self) -> None:
        """Удаление заказа вместе с позициями."""
        products, customers = self._make_products_and_customers()
        order = Order(customers[0])
        order.add_item(products[0], 1)
        self.db.add_order(order)
        self.db.delete_order(order.order_id)
        self.assertEqual(self.db.get_all_orders(), [])

    def test_persistence_across_instances(self) -> None:
        """Данные сохраняются между запусками."""
        self._make_products_and_customers()
        reopened = Database(self.db_path)
        self.assertEqual(len(reopened.get_all_products()), 2)
        self.assertEqual(len(reopened.get_all_customers()), 2)

    def test_json_round_trip(self) -> None:
        """Экспорт и импорт данных в формате JSON."""
        products, customers = self._make_products_and_customers()
        order = Order(customers[0], order_date="2026-06-01")
        order.add_item(products[0], 2)
        self.db.add_order(order)

        json_path = os.path.join(self.tmpdir, "dump.json")
        self.db.export_json(json_path)

        target = Database(os.path.join(self.tmpdir, "import.xlsx"))
        target.import_json(json_path)
        self.assertEqual(len(target.get_all_products()), 2)
        self.assertEqual(len(target.get_all_customers()), 2)
        self.assertEqual(len(target.get_all_orders()), 1)
        self.assertAlmostEqual(target.get_all_orders()[0].total(), 100000)

    def test_csv_export(self) -> None:
        """Экспорт заказов и клиентов в CSV."""
        products, customers = self._make_products_and_customers()
        order = Order(customers[0], order_date="2026-06-01")
        order.add_item(products[0], 1)
        self.db.add_order(order)

        orders_csv = os.path.join(self.tmpdir, "orders.csv")
        customers_csv = os.path.join(self.tmpdir, "customers.csv")
        self.db.export_orders_csv(orders_csv)
        self.db.export_customers_csv(customers_csv)
        with open(orders_csv, encoding="utf-8") as f:
            lines = f.read().strip().splitlines()
        self.assertEqual(len(lines), 2)  # шапка + 1 заказ
        with open(customers_csv, encoding="utf-8") as f:
            self.assertEqual(len(f.read().strip().splitlines()), 3)  # шапка + 2 клиента


if __name__ == "__main__":
    unittest.main()