"""Unit-тесты для модуля analysis.py.

Покрытие функций анализа заказов: топ клиентов, динамика,
граф связей, визуализация.
"""

from __future__ import annotations

import os
import tempfile
import unittest

import analysis
from models import Customer, Order, Product


def make_orders() -> list:
    """Создать набор тестовых заказов.

    Returns
    -------
    list[Order]
        Список заказов.
    """
    products = [
        Product("Ноутбук", 50000, "Электроника", product_id=1),
        Product("Книга", 1299, "Книги", product_id=2),
        Product("Чашка", 900, "Посуда", product_id=3),
    ]
    customers = [
        Customer("Иван", "ivan@example.com", "+7 (999) 123-45-67", "Москва", 1),
        Customer("Мария", "maria@example.com", "+7 (916) 555-23-41", "Москва", 2),
        Customer("Пётр", "petr@example.com", "8 (812) 333-12-45", "Спб", 3),
    ]
    orders = []

    order = Order(customers[0], order_date="2026-01-01")
    order.add_item(products[0], 1)
    orders.append(order)

    order = Order(customers[0], order_date="2026-01-10")
    order.add_item(products[1], 2)
    orders.append(order)

    order = Order(customers[1], order_date="2026-01-05")
    order.add_item(products[2], 3)
    orders.append(order)

    order = Order(customers[1], order_date="2026-02-01")
    order.add_item(products[0], 1)
    orders.append(order)

    order = Order(customers[2], order_date="2026-02-15")
    order.add_item(products[1], 1)
    orders.append(order)

    return orders


class TestAnalysisFunctions(unittest.TestCase):
    """Тесты функций анализа."""

    def setUp(self) -> None:
        """Подготовка данных для тестов."""
        self.orders = make_orders()

    def test_orders_dataframe(self) -> None:
        """Проверка преобразования заказов в DataFrame."""
        df = analysis.orders_dataframe(self.orders)
        self.assertEqual(len(df), 5)
        self.assertEqual(df["date"].dtype.kind, "M")
        self.assertAlmostEqual(df["total"].sum(), 50000 + 2598 + 2700 + 50000 + 1299)

    def test_top_customers(self) -> None:
        """Топ клиентов по числу заказов."""
        top = analysis.top_customers(self.orders)
        self.assertEqual(len(top), 3)
        self.assertEqual(top[0][0].name, "Иван")
        self.assertEqual(top[0][1], 2)

    def test_top_customers_top_n(self) -> None:
        """Параметр top_n ограничивает количество."""
        top = analysis.top_customers(self.orders, top_n=1)
        self.assertEqual(len(top), 1)

    def test_top_customers_by_total(self) -> None:
        """Топ клиентов по сумме заказов."""
        top = analysis.top_customers_by_total(self.orders)
        self.assertEqual(top[0][0].name, "Мария")
        self.assertAlmostEqual(top[0][1], 52700)

    def test_orders_by_date(self) -> None:
        """Динамика заказов по датам."""
        df = analysis.orders_by_date(self.orders)
        self.assertGreaterEqual(len(df), 3)
        total_count = df["count"].sum()
        self.assertEqual(total_count, 5)

    def test_top_products(self) -> None:
        """Топ товаров по количеству продаж."""
        top = analysis.top_products(self.orders)
        self.assertEqual(top[0][0], "Книга")
        self.assertEqual(top[0][1], 3)

    def test_sales_by_category(self) -> None:
        """Выручка по категориям."""
        categories = analysis.sales_by_category(self.orders)
        self.assertAlmostEqual(sum(categories.values), 50000 + 2598 + 2700 + 50000 + 1299)
        self.assertTrue("Электроника" in categories.index)

    def test_empty_orders_dataframe(self) -> None:
        """Пустой список заказов."""
        df = analysis.orders_dataframe([])
        self.assertTrue(df.empty)

    def test_empty_top_customers(self) -> None:
        """Топ клиентов при пустом списке."""
        self.assertEqual(analysis.top_customers([]), [])

    def test_build_social_graph(self) -> None:
        """Построение графа связей клиентов."""
        graph = analysis.build_social_graph(self.orders)
        self.assertEqual(graph.number_of_nodes(), 3)
        self.assertTrue(graph.has_node("Иван"))
        self.assertTrue(graph.has_node("Мария"))
        self.assertTrue(graph.has_edge("Иван", "Мария"))


class TestPlots(unittest.TestCase):
    """Тесты сохранения графиков."""

    def setUp(self) -> None:
        """Подготовка данных и временной директории."""
        self.orders = make_orders()
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self) -> None:
        """Очистка временной директории."""
        for name in os.listdir(self.tmpdir):
            os.remove(os.path.join(self.tmpdir, name))
        os.rmdir(self.tmpdir)

    def _assert_png(self, path: str) -> None:
        """Проверить, что файл является корректным PNG-изображением."""
        self.assertTrue(os.path.exists(path))
        with open(path, "rb") as f:
            header = f.read(8)
        self.assertEqual(header[:4], b"\x89PNG")

    def test_save_plot_top_customers(self) -> None:
        """Сохранение графика топ клиентов."""
        path = os.path.join(self.tmpdir, "top.png")
        result = analysis.save_plot_top_customers(self.orders, path)
        self._assert_png(result)

    def test_save_plot_orders_dynamics(self) -> None:
        """Сохранение графика динамики."""
        path = os.path.join(self.tmpdir, "dyn.png")
        result = analysis.save_plot_orders_dynamics(self.orders, path)
        self._assert_png(result)

    def test_save_plot_top_products(self) -> None:
        """Сохранение графика топ товаров."""
        path = os.path.join(self.tmpdir, "prod.png")
        result = analysis.save_plot_top_products(self.orders, path)
        self._assert_png(result)

    def test_save_plot_sales_by_category(self) -> None:
        """Сохранение графика по категориям."""
        path = os.path.join(self.tmpdir, "cat.png")
        result = analysis.save_plot_sales_by_category(self.orders, path)
        self._assert_png(result)

    def test_save_plot_customer_graph(self) -> None:
        """Сохранение графа связей."""
        path = os.path.join(self.tmpdir, "graph.png")
        result = analysis.save_plot_customer_graph(self.orders, path)
        self._assert_png(result)

    def test_plot_empty_raises(self) -> None:
        """Пустые данные должны вызывать ValueError."""
        with self.assertRaises(ValueError):
            analysis.save_plot_top_customers([], "tmp.png")


if __name__ == "__main__":
    unittest.main()
