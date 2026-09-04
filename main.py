"""Точка входа в приложение.

Реализует запуск графического интерфейса и, при необходимости,
заполнение базы данных демонстрационными данными.

Запуск:
    python main.py --seed   # заполнить БД демо-данными
    python main.py          # обычный запуск
"""

from __future__ import annotations

import argparse
import sys


def seed_demo_data() -> None:
    """Заполнить базу данных демонстрационными данными.

    Creates
    -------
    Создаёт примеры товаров, клиентов и заказов в базе данных.

    Returns
    -------
    None
    """
    from db import Database
    from models import Customer, Order, Product

    db = Database("shop.db")

    if db.get_all_products():
        print("База данных уже содержит данные. Пропускаем заполнение.")
        return

    products = [
        Product("Ноутбук Lenovo", 58990, "Электроника"),
        Product("Смартфон Samsung", 34990, "Электроника"),
        Product("Наушники Sony", 12990, "Электроника"),
        Product("Книга «Python для всех»", 1299, "Книги"),
        Product("Кофемашина DeLonghi", 24990, "Бытовая техника"),
        Product("Микроволновая печь", 8990, "Бытовая техника"),
        Product("Футболка", 1290, "Одежда"),
        Product("Джинсы Levi's", 4990, "Одежда"),
    ]
    for p in products:
        db.add_product(p)

    customers = [
        Customer("Иван Петров", "ivan@example.com", "+7 (999) 123-45-67", "Москва"),
        Customer("Мария Смирнова", "maria@example.com", "+7 (916) 555-23-41", "Москва"),
        Customer("Пётр Иванов", "petr@example.com", "8 (812) 333-12-45", "Санкт-Петербург"),
        Customer("Анна Козлова", "anna@example.com", "+7 (495) 777-88-99", "Казань"),
        Customer("Сергей Морозов", "sergey@example.com", "+7 (900) 111-22-33", "Самара"),
        Customer("Ольга Волкова", "olga@example.com", "8 (800) 555-35-35", "Москва"),
        Customer("Дмитрий Соколов", "dmitry@example.com", "+7 (911) 222-33-44", "Екатеринбург"),
    ]
    for c in customers:
        db.add_customer(c)

    all_products = db.get_all_products()
    all_customers = db.get_all_customers()

    sample_orders = [
        (0, ["2026-06-01", "новый", [(0, 1), (4, 1)]]),
        (0, ["2026-06-05", "доставлен", [(1, 1), (2, 1)]]),
        (1, ["2026-06-10", "доставлен", [(0, 1), (3, 2)]]),
        (2, ["2026-06-12", "отправлен", [(2, 1)]]),
        (3, ["2026-06-15", "доставлен", [(5, 1), (6, 3)]]),
        (4, ["2026-06-20", "новый", [(4, 1), (7, 1)]]),
        (5, ["2026-06-22", "в обработке", [(1, 2), (2, 1)]]),
        (6, ["2026-06-25", "доставлен", [(0, 1)]]),
        (0, ["2026-07-01", "доставлен", [(6, 2), (7, 1)]]),
        (1, ["2026-07-05", "отправлен", [(3, 1)]]),
        (2, ["2026-07-08", "новый", [(5, 1)]]),
        (3, ["2026-07-12", "доставлен", [(0, 1), (4, 2)]]),
        (5, ["2026-07-15", "доставлен", [(6, 1)]]),
        (4, ["2026-07-18", "в обработке", [(2, 2), (3, 3)]]),
    ]

    for cust_idx, (info) in sample_orders:
        order_date, status, items = info
        customer = all_customers[cust_idx]
        order = Order(customer, order_date=order_date, status=status)
        for prod_idx, quantity in items:
            order.add_item(all_products[prod_idx], quantity)
        db.add_order(order)

    print(f"Демо-данные добавлены: {len(all_products)} товаров, "
          f"{len(all_customers)} клиентов, {len(sample_orders)} заказов.")


def main() -> None:
    """Основная функция запуска приложения.

    Returns
    -------
    None
    """
    parser = argparse.ArgumentParser(description="Система учёта заказов интернет-магазина")
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Заполнить базу данных демонстрационными данными",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Запустить unit-тесты",
    )
    args = parser.parse_args()

    if args.test:
        import unittest

        suite = unittest.defaultTestLoader.discover("tests")
        runner = unittest.TextTestRunner()
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)

    try:
        if args.seed:
            seed_demo_data()
        import gui

        gui.run()
    except KeyboardInterrupt:
        print("\nПрограмма завершена пользователем.")
    except Exception as exc:  # noqa: BLE001
        print(f"Ошибка запуска: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
