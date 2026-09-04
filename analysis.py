"""Анализ и визуализация данных.

Модуль содержит функции для анализа заказов и клиентов,
а также функции построения графиков с использованием
pandas, matplotlib, seaborn и networkx.
"""

from __future__ import annotations

import os
from collections import Counter, defaultdict
from typing import List, Tuple

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import seaborn as sns

from models import Customer, Order


def orders_dataframe(orders: List[Order]) -> pd.DataFrame:
    """Преобразовать список заказов в DataFrame pandas.

    Parameters
    ----------
    orders : list[Order]
        Список заказов.

    Returns
    -------
    pandas.DataFrame
        Таблица с полями order_id, date, customer, city, status, total.
    """
    rows = []
    for order in orders:
        rows.append(
            {
                "order_id": order.order_id,
                "date": pd.to_datetime(order.order_date),
                "customer": order.customer.name,
                "city": order.customer.city,
                "status": order.status,
                "total": order.total(),
            }
        )
    return pd.DataFrame(rows)


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


def orders_by_date(orders: List[Order]) -> pd.DataFrame:
    """Получить динамику числа заказов по датам.

    Parameters
    ----------
    orders : list[Order]
        Список заказов.

    Returns
    -------
    pandas.DataFrame
        Таблица с количеством заказов и суммой по датам.
    """
    df = orders_dataframe(orders)
    if df.empty:
        return pd.DataFrame(columns=["date", "count", "sum"])
    grouped = (
        df.groupby(df["date"].dt.date)
        .agg(count=("total", "size"), sum=("total", "sum"))
        .reset_index()
    )
    return grouped.sort_values("date")


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


def sales_by_category(orders: List[Order]) -> pd.Series:
    """Продажи по категориям товаров.

    Parameters
    ----------
    orders : list[Order]
        Список заказов.

    Returns
    -------
    pandas.Series
        Сумма выручки по категориям.
    """
    category_revenue = defaultdict(float)
    for order in orders:
        for item in order.items:
            category_revenue[item.product.category] += item.subtotal()
    return pd.Series(category_revenue).sort_values(ascending=False)


def build_social_graph(orders: List[Order]) -> nx.Graph:
    """Построить граф связей клиентов.

    Клиенты соединяются ребром, если у них общий город
    или они покупали общие товары.

    Parameters
    ----------
    orders : list[Order]
        Список заказов.

    Returns
    -------
    networkx.Graph
        Граф, вершины — клиенты, рёбра — общие связи.
    """
    graph = nx.Graph()
    customers = {order.customer for order in orders}
    for customer in customers:
        graph.add_node(customer.name, city=customer.city)

    city_groups: dict = defaultdict(list)
    for customer in customers:
        city_groups[customer.city].append(customer.name)
    for members in city_groups.values():
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                if graph.has_edge(members[i], members[j]):
                    graph[members[i]][members[j]]["weight"] += 1
                else:
                    graph.add_edge(members[i], members[j], weight=1)

    product_buyers: dict = defaultdict(list)
    for order in orders:
        for item in order.items:
            product_buyers[item.product.name].append(order.customer.name)
    for buyers in product_buyers.values():
        unique_buyers = list(dict.fromkeys(buyers))
        for i in range(len(unique_buyers)):
            for j in range(i + 1, len(unique_buyers)):
                if graph.has_edge(unique_buyers[i], unique_buyers[j]):
                    graph[unique_buyers[i]][unique_buyers[j]]["weight"] += 1
                else:
                    graph.add_edge(unique_buyers[i], unique_buyers[j], weight=0.5)

    return graph


def save_plot_top_customers(orders: List[Order], path: str) -> str:
    """Сохранить график топ клиентов по числу заказов.

    Parameters
    ----------
    orders : list[Order]
        Список заказов.
    path : str
        Путь к сохраняемому изображению.

    Returns
    -------
    str
        Путь к сохранённому изображению.
    """
    data = top_customers(orders, top_n=5)
    if not data:
        raise ValueError("Нет данных для построения графика")
    plt.figure(figsize=(8, 5))
    names = [c.name for c, _ in data]
    counts = [cnt for _, cnt in data]
    sns.barplot(x=names, y=counts, hue=names, palette="viridis", legend=False)
    plt.title("Топ 5 клиентов по числу заказов")
    plt.xlabel("Клиент")
    plt.ylabel("Число заказов")
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()
    return path


def save_plot_orders_dynamics(orders: List[Order], path: str) -> str:
    """Сохранить график динамики числа заказов по датам.

    Parameters
    ----------
    orders : list[Order]
        Список заказов.
    path : str
        Путь к сохраняемому изображению.

    Returns
    -------
    str
        Путь к сохранённому изображению.
    """
    df = orders_by_date(orders)
    if df.empty:
        raise ValueError("Нет данных для построения графика")
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=df, x="date", y="count", marker="o")
    plt.title("Динамика количества заказов по датам")
    plt.xlabel("Дата")
    plt.ylabel("Число заказов")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()
    return path


def save_plot_top_products(orders: List[Order], path: str) -> str:
    """Сохранить график топ товаров по количеству проданных штук.

    Parameters
    ----------
    orders : list[Order]
        Список заказов.
    path : str
        Путь к сохраняемому изображению.

    Returns
    -------
    str
        Путь к сохранённому изображению.
    """
    data = top_products(orders, top_n=5)
    if not data:
        raise ValueError("Нет данных для построения графика")
    plt.figure(figsize=(8, 5))
    names = [name for name, _ in data]
    qty = [q for _, q in data]
    sns.barplot(x=qty, y=names, hue=names, palette="magma", legend=False, orient="h")
    plt.title("Топ 5 товаров по количеству продаж")
    plt.xlabel("Количество штук")
    plt.ylabel("Товар")
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()
    return path


def save_plot_sales_by_category(orders: List[Order], path: str) -> str:
    """Сохранить график выручки по категориям.

    Parameters
    ----------
    orders : list[Order]
        Список заказов.
    path : str
        Путь к сохраняемому изображению.

    Returns
    -------
    str
        Путь к сохранённому изображению.
    """
    categories = sales_by_category(orders)
    if categories.empty:
        raise ValueError("Нет данных для построения графика")
    plt.figure(figsize=(8, 5))
    plt.pie(
        categories.values,
        labels=categories.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=sns.color_palette("Set2"),
    )
    plt.title("Выручка по категориям товаров")
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()
    return path


def save_plot_customer_graph(orders: List[Order], path: str) -> str:
    """Сохранить граф связей клиентов.

    Parameters
    ----------
    orders : list[Order]
        Список заказов.
    path : str
        Путь к сохраняемому изображению.

    Returns
    -------
    str
        Путь к сохранённому изображению.
    """
    graph = build_social_graph(orders)
    if graph.number_of_nodes() == 0:
        raise ValueError("Нет данных для построения графа")
    plt.figure(figsize=(10, 7))
    pos = nx.spring_layout(graph, seed=42)
    weights = [graph[u][v].get("weight", 1) for u, v in graph.edges()]
    nx.draw_networkx_nodes(
        graph, pos, node_size=600, node_color="lightblue", edgecolors="black"
    )
    nx.draw_networkx_edges(graph, pos, width=[w * 1.5 for w in weights], alpha=0.6)
    nx.draw_networkx_labels(graph, pos, font_size=9)
    plt.title("Граф связей клиентов (город / общие товары)")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()
    return path
