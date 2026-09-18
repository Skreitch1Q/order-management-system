from __future__ import annotations

import math
import tkinter as tk
from typing import List, Tuple

from analysis import Graph

# Палитра цветов для диаграмм.
PALETTE = [
    "#4C72B0",
    "#DD8452",
    "#55A868",
    "#C44E52",
    "#8172B3",
    "#937860",
    "#DA8BC3",
    "#64B5CD",
]

FONT_TITLE = ("Arial", 15, "bold")
FONT_LABEL = ("Arial", 10)


def create_chart_window(root: tk.Widget, title: str, width: int = 780, height: int = 520) -> Tuple[tk.Toplevel, tk.Canvas]:
    """Создать окно с холстом для диаграммы.

    Parameters
    ----------
    root : tk.Widget
        Родительский виджет.
    title : str
        Заголовок окна.
    width : int, optional
        Ширина окна (по умолчанию 780).
    height : int, optional
        Высота окна (по умолчанию 520).

    Returns
    -------
    tuple[tk.Toplevel, tk.Canvas]
        Окно и холст для рисования.
    """
    window = tk.Toplevel(root)
    window.title(title)
    window.geometry(f"{width}x{height}")
    canvas = tk.Canvas(window, width=width, height=height, bg="white")
    canvas.pack(fill="both", expand=True)
    return window, canvas


def draw_bar_chart(canvas: tk.Canvas, labels: List[str], values: List[float], title: str) -> None:
    """Нарисовать столбчатую диаграмму.

    Parameters
    ----------
    canvas : tk.Canvas
        Холст для рисования.
    labels : list[str]
        Подписи столбцов.
    values : list[float]
        Значения столбцов.
    title : str
        Заголовок диаграммы.
    """
    canvas.delete("all")
    width = int(canvas["width"])
    height = int(canvas["height"])
    margin_l, margin_r, margin_t, margin_b = 80, 30, 70, 80

    max_value = max(values) if values else 1
    if max_value == 0:
        max_value = 1
    plot_w = width - margin_l - margin_r
    plot_h = height - margin_t - margin_b

    canvas.create_text(width / 2, 28, text=title, font=FONT_TITLE)
    canvas.create_line(margin_l, height - margin_b, width - margin_r, height - margin_b, fill="#555")
    canvas.create_line(margin_l, height - margin_b, margin_l, margin_t, fill="#555")

    count = len(labels)
    slot = plot_w / count if count else 1
    bar_width = slot * 0.62

    for i, (label, value) in enumerate(zip(labels, values)):
        bar_h = plot_h * value / max_value
        x0 = margin_l + slot * i + (slot - bar_width) / 2
        y0 = height - margin_b - bar_h
        color = PALETTE[i % len(PALETTE)]
        canvas.create_rectangle(
            x0, y0, x0 + bar_width, height - margin_b, fill=color, outline=""
        )
        if bar_h > 16:
            canvas.create_text(
                x0 + bar_width / 2, y0 + 12, text=f"{value:g}", font=FONT_LABEL, fill="white"
            )
        canvas.create_text(
            margin_l + slot * (i + 0.5),
            height - margin_b + 16,
            text=_ellipsize(label, 28),
            anchor="n",
            font=FONT_LABEL,
        )

    for k in range(6):
        value = max_value * k / 5
        y = height - margin_b - plot_h * k / 5
        canvas.create_line(margin_l - 4, y, margin_l, y, fill="#555")
        canvas.create_text(
            margin_l - 10, y, text=f"{value:g}", anchor="e", font=FONT_LABEL
        )


def draw_line_chart(canvas: tk.Canvas, labels: List[str], values: List[float], title: str) -> None:
    """Нарисовать линейную диаграмму динамики.

    Parameters
    ----------
    canvas : tk.Canvas
        Холст для рисования.
    labels : list[str]
        Подписи точек по оси X.
    values : list[float]
        Значения точек.
    title : str
        Заголовок диаграммы.
    """
    canvas.delete("all")
    width = int(canvas["width"])
    height = int(canvas["height"])
    margin_l, margin_r, margin_t, margin_b = 80, 50, 70, 80

    if not values:
        canvas.create_text(width / 2, height / 2, text="Нет данных", font=FONT_LABEL)
        return
    max_value = max(values)
    if max_value == 0:
        max_value = 1
    plot_w = width - margin_l - margin_r
    plot_h = height - margin_t - margin_b

    canvas.create_text(width / 2, 28, text=title, font=FONT_TITLE)
    canvas.create_line(margin_l, height - margin_b, width - margin_r, height - margin_b, fill="#555")
    canvas.create_line(margin_l, height - margin_b, margin_l, margin_t, fill="#555")

    count = len(values)
    step = plot_w / (count - 1) if count > 1 else 0
    points = []
    for i, (label, value) in enumerate(zip(labels, values)):
        x = margin_l + step * i
        y = height - margin_b - plot_h * value / max_value
        points.append((x, y))
        color = PALETTE[i % len(PALETTE)]
        canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill=color, outline="")
        canvas.create_text(x, y + 16, text=f"{value:g}", font=FONT_LABEL)
        canvas.create_text(x, height - margin_b + 16, text=_ellipsize(label, 14), anchor="n",
                           font=FONT_LABEL)

    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        canvas.create_line(x1, y1, x2, y2, fill="#4C72B0", width=3)

    for k in range(6):
        value = max_value * k / 5
        y = height - margin_b - plot_h * k / 5
        canvas.create_line(margin_l - 4, y, margin_l, y, fill="#555")
        canvas.create_text(margin_l - 10, y, text=f"{value:g}", anchor="e", font=FONT_LABEL)


def draw_pie_chart(canvas: tk.Canvas, labels: List[str], values: List[float], title: str) -> None:
    """Нарисовать круговую диаграмму долей.

    Parameters
    ----------
    canvas : tk.Canvas
        Холст для рисования.
    labels : list[str]
        Категории.
    values : list[float]
        Значения категорий.
    title : str
        Заголовок диаграммы.
    """
    canvas.delete("all")
    width = int(canvas["width"])
    height = int(canvas["height"])

    total = sum(values)
    if total <= 0:
        canvas.create_text(width / 2, height / 2, text="Нет данных", font=FONT_LABEL)
        return

    canvas.create_text(width / 2, 30, text=title, font=FONT_TITLE)

    center_x = width * 0.38
    center_y = height * 0.52
    radius = min(width, height) * 0.32

    start = 90.0
    for i, (label, value) in enumerate(zip(labels, values)):
        extent = -360.0 * value / total
        color = PALETTE[i % len(PALETTE)]
        canvas.create_arc(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            start=start,
            extent=extent,
            style="pieslice",
            fill=color,
            outline="white",
        )
        start += extent

    legend_x = width * 0.75
    legend_y = height * 0.18
    for i, (label, value) in enumerate(zip(labels, values)):
        color = PALETTE[i % len(PALETTE)]
        y = legend_y + i * 26
        canvas.create_rectangle(legend_x - 40, y - 8, legend_x - 18, y + 8, fill=color, outline="")
        percent = 100.0 * value / total
        canvas.create_text(
            legend_x,
            y,
            text=f"{_ellipsize(label, 22)} — {value:g} ({percent:.1f}%)",
            anchor="w",
            font=FONT_LABEL,
        )


def draw_customer_graph(canvas: tk.Canvas, graph: Graph, title: str) -> None:
    """Нарисовать граф связей клиентов.

    Вершины располагаются по кругу, толщина ребра пропорциональна весу.

    Parameters
    ----------
    canvas : tk.Canvas
        Холст для рисования.
    graph : Graph
        Граф связей клиентов.
    title : str
        Заголовок окна.
    """
    canvas.delete("all")
    width = int(canvas["width"])
    height = int(canvas["height"])
    canvas.create_text(width / 2, 28, text=title, font=FONT_TITLE)

    nodes = graph.nodes()
    if not nodes:
        canvas.create_text(width / 2, height / 2, text="Нет данных", font=FONT_LABEL)
        return

    center_x, center_y = width / 2, height / 2
    radius = min(width, height) / 2 - 90
    node_radius = 34

    positions = {}
    for i, node in enumerate(nodes):
        angle = 2 * math.pi * i / len(nodes) - math.pi / 2
        positions[node] = (
            center_x + radius * math.cos(angle),
            center_y + radius * math.sin(angle),
        )

    max_weight = max(w for _, _, w in graph.edges()) if graph.edges() else 1
    for u, v, weight in graph.edges():
        x1, y1 = positions[u]
        x2, y2 = positions[v]
        line_width = 1 + 3 * weight / max_weight
        canvas.create_line(x1, y1, x2, y2, fill="#999999", width=line_width)

    for node in nodes:
        x, y = positions[node]
        color = PALETTE[hash(node) % len(PALETTE)]
        canvas.create_oval(
            x - node_radius,
            y - node_radius,
            x + node_radius,
            y + node_radius,
            fill="lightblue",
            outline=color,
            width=2,
        )
        canvas.create_text(x, y, text=_ellipsize(node, 16), font=FONT_LABEL)


def _ellipsize(text: str, max_chars: int) -> str:
    """Сократить длинный текст до заданной длины.

    Parameters
    ----------
    text : str
        Исходный текст.
    max_chars : int
        Максимальная длина строки.

    Returns
    -------
    str
        Сокращённый текст.
    """
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1] + "…"