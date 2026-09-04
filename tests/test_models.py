"""Unit-тесты для модуля models.py.

Покрытие классов Product, Customer, Order и функций валидации.
"""

from __future__ import annotations

import unittest

from models import Customer, Order, OrderItem, Product


class TestProduct(unittest.TestCase):
    """Тесты класса Product."""

    def test_product_creation(self) -> None:
        """Проверка создания товара."""
        product = Product("Ноутбук", 50000, "Электроника")
        self.assertEqual(product.name, "Ноутбук")
        self.assertEqual(product.price, 50000)
        self.assertEqual(product.category, "Электроника")
        self.assertIsNone(product.product_id)

    def test_product_negative_price_raises(self) -> None:
        """Отрицательная цена должна вызывать исключение."""
        product = Product("Тест", 100, "Категория")
        with self.assertRaises(ValueError):
            product.price = -5

    def test_product_to_dict(self) -> None:
        """Проверка преобразования товара в словарь."""
        product = Product("Книга", 1299, "Книги", product_id=7)
        data = product.to_dict()
        self.assertEqual(data["product_id"], 7)
        self.assertEqual(data["name"], "Книга")
        self.assertEqual(data["price"], 1299)
        self.assertEqual(data["category"], "Книги")

    def test_product_from_dict(self) -> None:
        """Проверка создания товара из словаря."""
        data = {"name": "Чашка", "price": "900", "category": "Посуда", "product_id": 3}
        product = Product.from_dict(data)
        self.assertEqual(product.name, "Чашка")
        self.assertEqual(product.price, 900)
        self.assertEqual(product.category, "Посуда")
        self.assertEqual(product.product_id, 3)


class TestCustomer(unittest.TestCase):
    """Тесты класса Customer."""

    def test_customer_creation(self) -> None:
        """Проверка создания клиента."""
        customer = Customer("Иван", "ivan@example.com", "+7 (999) 123-45-67", "Москва")
        self.assertEqual(customer.name, "Иван")
        self.assertEqual(customer.email, "ivan@example.com")
        self.assertEqual(customer.city, "Москва")

    def test_invalid_email_raises(self) -> None:
        """Некорректный email должен вызывать исключение."""
        with self.assertRaises(ValueError):
            Customer("Иван", "не-email", "+7 (999) 123-45-67", "Москва")

    def test_invalid_phone_raises(self) -> None:
        """Некорректный телефон должен вызывать исключение."""
        with self.assertRaises(ValueError):
            Customer("Иван", "ivan@example.com", "12345", "Москва")

    def test_empty_email_raises(self) -> None:
        """Пустой email должен вызывать исключение."""
        with self.assertRaises(ValueError):
            Customer("Иван", "  ", "+7 (999) 123-45-67", "Москва")

    def test_to_dict(self) -> None:
        """Проверка преобразования клиента в словарь."""
        customer = Customer("Иван", "ivan@example.com", "+7 (999) 123-45-67", "Москва", 2)
        data = customer.to_dict()
        self.assertEqual(data["customer_id"], 2)
        self.assertEqual(data["name"], "Иван")
        self.assertEqual(data["city"], "Москва")

    def test_phone_variants(self) -> None:
        """Проверка различных допустимых форматов телефонов."""
        for phone in ["+7 (999) 123-45-67", "8 999 123 45 67", "89991234567"]:
            with self.subTest(phone=phone):
                customer = Customer("Иван", "ivan@example.com", phone, "Москва")
                self.assertEqual(customer.phone, phone)


class TestOrder(unittest.TestCase):
    """Тесты класса Order."""

    def setUp(self) -> None:
        """Создание общих объектов для тестов."""
        self.product_a = Product("A", 100, "Категория", product_id=1)
        self.product_b = Product("B", 250, "Категория", product_id=2)
        self.customer = Customer(
            "Анна", "anna@example.com", "+7 (495) 777-88-99", "Казань", customer_id=1
        )

    def test_order_total(self) -> None:
        """Проверка суммы заказа."""
        order = Order(self.customer)
        order.add_item(self.product_a, 2)
        order.add_item(self.product_b, 1)
        self.assertAlmostEqual(order.total(), 100 * 2 + 250 * 1)
        self.assertEqual(order.items_count(), 3)

    def test_order_item_subtotal(self) -> None:
        """Проверка стоимости позиции."""
        item = OrderItem(self.product_a, 3)
        self.assertEqual(item.subtotal(), 300)

    def test_default_date_and_status(self) -> None:
        """Проверка значений по умолчанию."""
        order = Order(self.customer)
        self.assertEqual(order.status, "новый")
        self.assertTrue(order.order_date)

    def test_status_setter(self) -> None:
        """Проверка установки статуса."""
        order = Order(self.customer)
        order.status = "доставлен"
        self.assertEqual(order.status, "доставлен")

    def test_quantity_positive(self) -> None:
        """Количество в позиции должно быть положительным."""
        order = Order(self.customer)
        order.add_item(self.product_a, 1)
        with self.assertRaises(ValueError):
            order.items[0].quantity = -1

    def test_order_to_dict(self) -> None:
        """Проверка преобразования заказа в словарь."""
        order = Order(self.customer, order_date="2026-01-01", status="новый", order_id=5)
        order.add_item(self.product_a, 2)
        data = order.to_dict()
        self.assertEqual(data["order_id"], 5)
        self.assertEqual(data["order_date"], "2026-01-01")
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(data["total"], 200)

    def test_polymorphism_to_dict(self) -> None:
        """Полиморфизм: все модели преобразуются в словарь одинаково."""
        for obj in [self.product_a, self.customer]:
            self.assertIsInstance(obj.to_dict(), dict)


if __name__ == "__main__":
    unittest.main()
