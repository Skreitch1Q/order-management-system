"""Модели данных системы учёта заказов.

В этом модуле определены классы товара, клиента и заказа.
Демонстрируются принципы ООП: инкапсуляция, наследование, полиморфизм.
"""

from __future__ import annotations

import re
from datetime import date
from typing import List, Optional

# Отдельные классы: Product, Customer, Order (могут быть изменены)

# Регулярные выражения для валидации контактных данных.
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_RE = re.compile(r"^(\+7|8)[\s\-]?(\(\d{3}\)|\d{3})[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$")


class ValidatedField:
    """Базовый класс-проверщик полей (инкапсуляция логики валидации)."""

    def validate(self, value: str) -> str:
        """Проверить и вернуть значение.

        Parameters
        ----------
        value : str
            Значение для проверки.

        Returns
        -------
        str
            Проверенное значение.

        Raises
        ------
        ValueError
            Если значение не прошло проверку.
        """
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Значение не должно быть пустым")
        return value.strip()


class EmailField(ValidatedField):
    """Проверка адреса электронной почты."""

    def validate(self, value: str) -> str:
        """Проверить корректность адреса электронной почты.

        Parameters
        ----------
        value : str
            Адрес электронной почты.

        Returns
        -------
        str
            Корректный адрес электронной почты.

        Raises
        ------
        ValueError
            Если адрес не соответствует регулярному выражению.
        """
        value = super().validate(value)
        if not EMAIL_RE.match(value):
            raise ValueError(f"Некорректный email: {value}")
        return value


class PhoneField(ValidatedField):
    """Проверка номера телефона."""

    def validate(self, value: str) -> str:
        """Проверить корректность номера телефона.

        Parameters
        ----------
        value : str
            Номер телефона.

        Returns
        -------
        str
            Корректный номер телефона.

        Raises
        ------
        ValueError
            Если номер не соответствует регулярному выражению.
        """
        value = super().validate(value)
        if not PHONE_RE.match(value):
            raise ValueError(f"Некорректный номер телефона: {value}")
        return value


class Product:
    """Товар интернет-магазина.

    Parameters
    ----------
    name : str
        Название товара.
    price : float
        Цена за единицу.
    category : str
        Категория товара.
    product_id : int, optional
        Идентификатор товара в базе.
    """

    def __init__(self, name: str, price: float, category: str, product_id: Optional[int] = None) -> None:
        self._product_id = product_id
        self._name = name
        self._price = price
        self._category = category

    @property
    def product_id(self) -> Optional[int]:
        """int: идентификатор товара."""
        return self._product_id

    @product_id.setter
    def product_id(self, value: int) -> None:
        self._product_id = value

    @property
    def name(self) -> str:
        """str: название товара."""
        return self._name

    @property
    def price(self) -> float:
        """float: цена за единицу."""
        return self._price

    @price.setter
    def price(self, value: float) -> None:
        if value < 0:
            raise ValueError("Цена не может быть отрицательной")
        self._price = value

    @property
    def category(self) -> str:
        """str: категория товара."""
        return self._category

    def __str__(self) -> str:
        """Строковое представление товара."""
        return f"Product({self.name}, {self.price} руб., {self.category})"

    def __repr__(self) -> str:
        """Техническое представление товара."""
        return self.__str__()

    def to_dict(self) -> dict:
        """Преобразовать товар в словарь.

        Returns
        -------
        dict
            Словарь с полями товара.
        """
        return {
            "product_id": self._product_id,
            "name": self._name,
            "price": self._price,
            "category": self._category,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        """Создать товар из словаря.

        Parameters
        ----------
        data : dict
            Словарь с полями товара.

        Returns
        -------
        Product
            Экземпляр товара.
        """
        return cls(
            name=data["name"],
            price=float(data["price"]),
            category=data["category"],
            product_id=data.get("product_id"),
        )


class Customer:
    """Клиент интернет-магазина.

    Parameters
    ----------
    name : str
        Имя клиента.
    email : str
        Адрес электронной почты.
    phone : str
        Номер телефона.
    city : str
        Город проживания.
    customer_id : int, optional
        Идентификатор клиента в базе.
    """

    def __init__(
        self,
        name: str,
        email: str,
        phone: str,
        city: str,
        customer_id: Optional[int] = None,
    ) -> None:
        self._customer_id = customer_id
        self._name = name
        self._email = EmailField().validate(email)
        self._phone = PhoneField().validate(phone)
        self._city = city

    @property
    def customer_id(self) -> Optional[int]:
        """int: идентификатор клиента."""
        return self._customer_id

    @customer_id.setter
    def customer_id(self, value: int) -> None:
        self._customer_id = value

    @property
    def name(self) -> str:
        """str: имя клиента."""
        return self._name

    @property
    def email(self) -> str:
        """str: адрес электронной почты."""
        return self._email

    @property
    def phone(self) -> str:
        """str: номер телефона."""
        return self._phone

    @property
    def city(self) -> str:
        """str: город проживания."""
        return self._city

    def __str__(self) -> str:
        """Строковое представление клиента."""
        return f"Customer({self.name}, {self.city}, {self.email})"

    def __repr__(self) -> str:
        """Техническое представление клиента."""
        return self.__str__()

    def to_dict(self) -> dict:
        """Преобразовать клиента в словарь.

        Returns
        -------
        dict
            Словарь с полями клиента.
        """
        return {
            "customer_id": self._customer_id,
            "name": self._name,
            "email": self._email,
            "phone": self._phone,
            "city": self._city,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Customer":
        """Создать клиента из словаря.

        Parameters
        ----------
        data : dict
            Словарь с полями клиента.

        Returns
        -------
        Customer
            Экземпляр клиента.
        """
        return cls(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            city=data["city"],
            customer_id=data.get("customer_id"),
        )


class OrderItem:
    """Позиция в заказе (товар и количество).

    Parameters
    ----------
    product : Product
        Товар.
    quantity : int
        Количество единиц.
    """

    def __init__(self, product: Product, quantity: int) -> None:
        self._product = product
        self._quantity = quantity

    @property
    def product(self) -> Product:
        """Product: товар позиции."""
        return self._product

    @property
    def quantity(self) -> int:
        """int: количество единиц."""
        return self._quantity

    @quantity.setter
    def quantity(self, value: int) -> None:
        if value <= 0:
            raise ValueError("Количество должно быть положительным")
        self._quantity = value

    def subtotal(self) -> float:
        """Стоимость позиции.

        Returns
        -------
        float
            Произведение цены товара на количество.
        """
        return self._product.price * self._quantity

    def __str__(self) -> str:
        """Строковое представление позиции."""
        return f"OrderItem({self.product.name} x {self.quantity})"

    def __repr__(self) -> str:
        """Техническое представление позиции."""
        return self.__str__()


class Order:
    """Заказ клиента.

    Parameters
    ----------
    customer : Customer
        Клиент, сделавший заказ.
    order_date : str
        Дата заказа в формате YYYY-MM-DD.
    items : list[OrderItem], optional
        Список позиций заказа.
    order_id : int, optional
        Идентификатор заказа в базе.
    status : str, optional
        Статус заказа.
    """

    def __init__(
        self,
        customer: Customer,
        order_date: Optional[str] = None,
        items: Optional[List[OrderItem]] = None,
        order_id: Optional[int] = None,
        status: str = "новый",
    ) -> None:
        self._order_id = order_id
        self._customer = customer
        self._order_date = order_date or date.today().isoformat()
        self._items: List[OrderItem] = items if items is not None else []
        self._status = status

    @property
    def order_id(self) -> Optional[int]:
        """int: идентификатор заказа."""
        return self._order_id

    @order_id.setter
    def order_id(self, value: int) -> None:
        self._order_id = value

    @property
    def customer(self) -> Customer:
        """Customer: клиент заказа."""
        return self._customer

    @property
    def order_date(self) -> str:
        """str: дата заказа в формате YYYY-MM-DD."""
        return self._order_date

    @property
    def items(self) -> List[OrderItem]:
        """list[OrderItem]: список позиций заказа."""
        return self._items

    @property
    def status(self) -> str:
        """str: статус заказа."""
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        self._status = value

    def add_item(self, product: Product, quantity: int) -> None:
        """Добавить позицию в заказ.

        Parameters
        ----------
        product : Product
            Товар для добавления.
        quantity : int
            Количество единиц.
        """
        self._items.append(OrderItem(product, quantity))

    def total(self) -> float:
        """Суммарная стоимость заказа.

        Returns
        -------
        float
            Сумма стоимости всех позиций.
        """
        return sum(item.subtotal() for item in self._items)

    def items_count(self) -> int:
        """Общее количество единиц товара в заказе.

        Returns
        -------
        int
            Сумма количеств всех позиций.
        """
        return sum(item.quantity for item in self._items)

    def __str__(self) -> str:
        """Строковое представление заказа."""
        return (
            f"Order(id={self.order_id}, {self.customer.name}, "
            f"{self.order_date}, {self.total():.2f} руб., {self.status})"
        )

    def __repr__(self) -> str:
        """Техническое представление заказа."""
        return self.__str__()

    def to_dict(self) -> dict:
        """Преобразовать заказ в словарь.

        Returns
        -------
        dict
            Словарь с полями заказа.
        """
        return {
            "order_id": self._order_id,
            "customer_id": self._customer.customer_id,
            "customer_name": self._customer.name,
            "order_date": self._order_date,
            "status": self._status,
            "total": self.total(),
            "items": [
                {
                    "product": item.product.to_dict(),
                    "quantity": item.quantity,
                    "subtotal": item.subtotal(),
                }
                for item in self._items
            ],
        }

    @classmethod
    def from_dict(cls, data: dict, customer: Customer, products: List[Product]) -> "Order":
        """Создать заказ из словаря.

        Parameters
        ----------
        data : dict
            Словарь с полями заказа.
        customer : Customer
            Клиент заказа.
        products : list[Product]
            Список всех товаров для сопоставления.

        Returns
        -------
        Order
            Экземпляр заказа.
        """
        order = cls(
            customer=customer,
            order_date=data.get("order_date"),
            status=data.get("status", "новый"),
            order_id=data.get("order_id"),
        )
        product_map = {p.product_id: p for p in products}
        for item in data.get("items", []):
            product = product_map.get(item["product"]["product_id"])
            if product is not None:
                order.add_item(product, item["quantity"])
        return order
