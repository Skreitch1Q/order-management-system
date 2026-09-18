from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

from models import Customer, Order


def orders_rows(orders: List[Order]) -> List[dict]:
    """Преобразовать список заказов в список словарей.

    Parameters
    ----------
    orders : list[Order]
        Список заказов.

    Returns
    -------
    list[dict]
        Строки с полями order_id, date, customer, city, status, total.
    """
    rows = []
    for order in orders:
        rows.append(
            {
                "order_id": order.order_id,
                "date": order.order_date,
                "customer": order.customer.name,
                "city": order.customer.city,
                "status": order.status,
                "total": order.total(),
            }
        )
    return rows


def total_revenue(orders: List[Order]) -> float:
    """Вычислить суммарную выручку всех заказов.

    Parameters
    ----------
    orders : list[Order]
        Список заказов.

    Returns
    -------
    float
        Сумма стоимостей всех заказов.
    """
    return sum(order.total() for order in orders)


def recursive_total(orders: List[Order], start: int = 0, end: Optional[int] = None) -> float:
    """Рекурсивно вычислить суммарную выручку заказов.

    Задача разбивается на две половины, каждая из которых
    вычисляется рекурсивно (метод «разделяй и властвуй»).

    Parameters
    ----------
    orders : list[Order]
        Список заказов.
    start : int, optional
        Индекс начала диапазона (по умолчанию 0).
    end : int, optional
        Индекс конца диапазона (по умолчанию len(orders)).

    Returns
    -------
    float
        Сумма стоимостей заказов в диапазоне [start, end).
    """
    if end is None:
        end = len(orders)
    if start >= end:
        return 0.0
    if end - start == 1:
        return orders[start].total()
    middle = (start + end) // 2
    return recursive_total(orders, start, middle) + recursive_total(orders, middle, end)


def top_customers(orders: List[Order], top_n: int = 5) -> List[Tuple[Customer, int]]:
    """Определить топ клиентов по числу заказов.

    Parameters
    ----------
    orders : list[Order]
        Список заказов.
    top_n : int, optional
        Количество клиентов в топе (по умолчанию 5).

    Returns
    -------
    list[tuple[Customer, int]]
        Список пар (клиент, число заказов), отсортированный по убыванию.
    """
    counts = Counter(order.customer for order in orders)
    return sorted(counts.items(), key=lambda item: item[1], reverse=True)[:top_n]


def top_customers_by_total(orders: List[Order], top_n: int = 5) -> List[Tuple[Customer, float]]:
    """Определить топ клиентов по суммарной стоимости заказов.

    Parameters
    ----------
    orders : list[Order]
        Список заказов.
    top_n : int, optional
        Количество клиентов в топе (по умолчанию 5).

    Returns
    -------
    list[tuple[Customer, float]]
        Список пар (клиент, суммарная стоимость), отсортированный по убыванию.
    """
    totals = defaultdict(float)
    for order in orders:
        totals[order.customer] += order.total()
    return sorted(totals.items(), key=lambda item: item[1], reverse=True)[:top_n]


def orders_by_date(orders: List[Order]) -> List[dict]:
    """Получить динамику числа заказов по датам.

    Parameters
    ----------
    orders : list[Order]
        Список заказов.

    Returns
    -------
    list[dict]
        Строки с полями date, count, sum, отсортированные по дате.
    """
    grouped: Dict[str, List[float]] = defaultdict(list)
    for order in orders:
        grouped[order.order_date].append(order.total())
    rows = []
    for order_date, totals in grouped.items():
        rows.append(
            {
                "date": order_date,
                "count": len(totals),
                "sum": sum(totals),
            }
        )
    return sorted(rows, key=lambda row: row["date"])


def top_products(orders: List[Order], top_n: int = 5) -> List[Tuple[str, int]]:
    """Определить самые продаваемые товары по количеству штук.

    Parameters
    ----------
    orders : list[Order]
        Список заказов.
    top_n : int, optional
        Количество товаров в топе (по умолчанию 5).

    Returns
    -------
    list[tuple[str, int]]
        Список пар (название товара, количество), отсортированный по убыванию.
    """
    counts = Counter()
    for order in orders:
        for item in order.items:
            counts[item.product.name] += item.quantity
    return counts.most_common(top_n)


def sales_by_category(orders: List[Order]) -> List[Tuple[str, float]]:
    """Выручка по категориям товаров.

    Parameters
    ----------
    orders : list[Order]
        Список заказов.

    Returns
    -------
    list[tuple[str, float]]
        Список пар (категория, выручка), отсортированный по убыванию.
    """
    category_revenue = defaultdict(float)
    for order in orders:
        for item in order.items:
            category_revenue[item.product.category] += item.subtotal()
    return sorted(category_revenue.items(), key=lambda item: item[1], reverse=True)


class Graph:
    """Простой неориентированный взвешенный граф.

    Реализован на чистом Python, используется для построения
    графа связей клиентов и его отрисовки на холсте tkinter.
    """

    def __init__(self) -> None:
        """"""
        self._nodes: set = set()
        self._edges: Dict[Tuple[str, str], float] = {}
        self._attributes: Dict[str, dict] = {}

    def add_node(self, node: str, **attributes) -> None:
        """Добавить вершину в граф.

        Parameters
        ----------
        node : str
            Имя вершины.
        **attributes
            Произвольные атрибуты вершины.
        """
        self._nodes.add(node)
        self._attributes.setdefault(node, {})
        self._attributes[node].update(attributes)

    def add_edge(self, source: str, target: str, weight: float = 1.0) -> None:
        """Добавить ребро между вершинами.

        Parameters
        ----------
        source : str
            Первая вершина ребра.
        target : str
            Вторая вершина ребра.
        weight : float, optional
            Вес ребра (по умолчанию 1.0).
        """
        self.add_node(source)
        self.add_node(target)
        key = (source, target) if source < target else (target, source)
        if key in self._edges:
            self._edges[key] += weight
        else:
            self._edges[key] = weight

    def nodes(self) -> List[str]:
        """Список вершин графа.

        Returns
        -------
        list[str]
            Имена вершин.
        """
        return list(self._nodes)

    def edges(self) -> List[Tuple[str, str, float]]:
        """Список рёбер графа.

        Returns
        -------
        list[tuple[str, str, float]]
            Тройки (вершина, вершина, вес).
        """
        return [(u, v, w) for (u, v), w in self._edges.items()]

    def node_count(self) -> int:
        """Количество вершин графа.

        Returns
        -------
        int
            Число вершин.
        """
        return len(self._nodes)

    def edge_count(self) -> int:
        """Количество рёбер графа.

        Returns
        -------
        int
            Число рёбер.
        """
        return len(self._edges)

    def attributes_of(self, node: str) -> dict:
        """Атрибуты вершины.

        Parameters
        ----------
        node : str
            Имя вершины.

        Returns
        -------
        dict
            Словарь атрибутов вершины.
        """
        return self._attributes.get(node, {})


def build_customer_graph(orders: List[Order]) -> Graph:
    """Построить граф связей клиентов.

    Клиенты соединяются ребром, если у них общий город
    или они покупали общие товары. Вес ребра равен числу общих связей.

    Parameters
    ----------
    orders : list[Order]
        Список заказов.

    Returns
    -------
    Graph
        Граф: вершины — клиенты, рёбра — общие связи.
    """
    graph = Graph()
    customers = {order.customer for order in orders}
    for customer in customers:
        graph.add_node(customer.name, city=customer.city)

    city_groups: Dict[str, List[str]] = defaultdict(list)
    for customer in customers:
        city_groups[customer.city].append(customer.name)
    for members in city_groups.values():
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                graph.add_edge(members[i], members[j], weight=1)

    product_buyers: Dict[str, List[str]] = defaultdict(list)
    for order in orders:
        for item in order.items:
            product_buyers[item.product.name].append(order.customer.name)
    for buyers in product_buyers.values():
        unique_buyers = list(dict.fromkeys(buyers))
        for i in range(len(unique_buyers)):
            for j in range(i + 1, len(unique_buyers)):
                graph.add_edge(unique_buyers[i], unique_buyers[j], weight=0.5)

    return graph