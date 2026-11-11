"""Генерация диаграмм D2 и сохранение графа в формате PNG (этап 5)."""

from __future__ import annotations

import math
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

Edge = tuple[str, str]
Point = tuple[int, int]
Positions = dict[str, Point]

D2_ARROW = "->"
D2_SUFFIX = ".d2"
PNG_SUFFIX = ".png"
QUOTE = '"'

CANVAS_PAD = 40
COL_WIDTH = 220
ROW_HEIGHT = 76
NODE_HALF_W = 80
NODE_HALF_H = 22
ARROW_LEN = 10
ARROW_ANGLE = 0.5
LINE_WIDTH = 2
EXIT_SUCCESS = 0
ZERO_DELTA = 0

BG_COLOR = (255, 255, 255)
BOX_FILL = (238, 244, 255)
BOX_BORDER = (55, 90, 160)
EDGE_COLOR = (90, 105, 130)
TEXT_COLOR = (20, 30, 50)


@dataclass(frozen=True)
class CanvasSpec:
    """Геометрия холста и узлов при отрисовке графа."""

    width: int
    height: int
    positions: Positions


def _quote_node(name: str) -> str:
    """Оборачивает идентификатор узла в кавычки для D2."""
    escaped = name.replace("\\", "\\\\").replace(QUOTE, f"\\{QUOTE}")
    return f"{QUOTE}{escaped}{QUOTE}"


def format_d2(edges: list[Edge], root: str = "") -> str:
    """Формирует текстовое представление графа на языке диаграмм D2."""
    if not edges:
        return _quote_node(root) + "\n" if root else ""
    lines = [
        f"{_quote_node(src)} {D2_ARROW} {_quote_node(dst)}"
        for src, dst in edges
    ]
    return "\n".join(lines) + "\n"


def d2_path_for(output_path: str) -> Path:
    """Возвращает путь к .d2 файлу рядом с выходным PNG."""
    return Path(output_path).with_suffix(D2_SUFFIX)


def save_d2(d2_text: str, output_path: str) -> Path:
    """Сохраняет описание графа на языке D2 в файл."""
    target = d2_path_for(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(d2_text, encoding="utf-8")
    return target


def render_png(
    edges: list[Edge],
    root: str,
    output_path: str,
) -> Path:
    """
    Формирует D2-описание и сохраняет изображение графа в PNG.

    Raises:
        ValueError: если выходной файл не имеет расширения .png.
    """
    out = Path(output_path)
    if out.suffix.lower() != PNG_SUFFIX:
        raise ValueError("выходной файл графа должен быть в формате .png")
    out.parent.mkdir(parents=True, exist_ok=True)
    d2_text = format_d2(edges, root)
    d2_file = save_d2(d2_text, output_path)
    if not _try_d2_cli(d2_file, out):
        _render_fallback_png(edges, root, out)
    return out


def _try_d2_cli(d2_file: Path, png_file: Path) -> bool:
    """Пытается скомпилировать .d2 в .png через утилиту d2."""
    d2_bin = shutil.which("d2")
    if d2_bin is None:
        return False
    result = subprocess.run(
        [d2_bin, str(d2_file), str(png_file)],
        capture_output=True,
        check=False,
    )
    return result.returncode == EXIT_SUCCESS and png_file.is_file()


def _collect_nodes(edges: list[Edge], root: str) -> list[str]:
    """Собирает упорядоченный список уникальных узлов графа."""
    seen: list[str] = []
    if root:
        seen.append(root)
    for src, dst in edges:
        if src not in seen:
            seen.append(src)
        if dst not in seen:
            seen.append(dst)
    return seen


def _assign_layers(edges: list[Edge], root: str) -> list[list[str]]:
    """Распределяет узлы по уровням удалённости от корня."""
    nodes = _collect_nodes(edges, root)
    if not nodes:
        return []
    levels: dict[str, int] = {nodes[0]: 0}
    for src, dst in edges:
        src_lvl = levels.setdefault(src, 0)
        if dst not in levels:
            levels[dst] = src_lvl + 1
    return _group_by_level(nodes, levels)


def _group_by_level(
    nodes: list[str],
    levels: dict[str, int],
) -> list[list[str]]:
    """Группирует узлы в список слоёв по номеру уровня."""
    max_lvl = max(levels.values(), default=0)
    layers: list[list[str]] = [[] for _ in range(max_lvl + 1)]
    for node in nodes:
        layers[levels.get(node, 0)].append(node)
    return [layer for layer in layers if layer]


def _build_layout(edges: list[Edge], root: str) -> CanvasSpec:
    """Вычисляет координаты центров узлов и размер холста."""
    layers = _assign_layers(edges, root)
    if not layers:
        layers = [[root or "empty"]]
    max_rows = max(len(layer) for layer in layers)
    width = CANVAS_PAD * 2 + len(layers) * COL_WIDTH
    height = CANVAS_PAD * 2 + max_rows * ROW_HEIGHT
    positions = _place_layers(layers, height)
    return CanvasSpec(width=width, height=height, positions=positions)


def _place_layers(layers: list[list[str]], height: int) -> Positions:
    """Расставляет узлы каждого слоя по вертикали."""
    positions: Positions = {}
    for col_idx, layer in enumerate(layers):
        cx = CANVAS_PAD + col_idx * COL_WIDTH + COL_WIDTH // 2
        step = (height - CANVAS_PAD * 2) // (len(layer) + 1)
        for row_idx, name in enumerate(layer, start=1):
            positions[name] = (cx, CANVAS_PAD + row_idx * step)
    return positions


def _render_fallback_png(
    edges: list[Edge],
    root: str,
    png_file: Path,
) -> None:
    """Рендерит PNG графа средствами Pillow, если d2 не установлен."""
    spec = _build_layout(edges, root)
    image = Image.new("RGB", (spec.width, spec.height), BG_COLOR)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    for src, dst in edges:
        _draw_edge(draw, spec.positions[src], spec.positions[dst])
    for name, center in spec.positions.items():
        _draw_node(draw, font, name, center)
    image.save(png_file, format="PNG")


def _draw_edge(draw: ImageDraw.ImageDraw, p1: Point, p2: Point) -> None:
    """Рисует направленное ребро со стрелкой между двумя узлами."""
    start, end = _clip_segment(p1, p2)
    draw.line([start, end], fill=EDGE_COLOR, width=LINE_WIDTH)
    _draw_arrowhead(draw, start, end)


def _clip_segment(p1: Point, p2: Point) -> tuple[Point, Point]:
    """Сдвигает концы ребра к границам прямоугольников узлов."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    if abs(dx) >= abs(dy) and dx != ZERO_DELTA:
        sign = 1 if dx > ZERO_DELTA else -1
        start = (p1[0] + sign * NODE_HALF_W, p1[1])
        end = (p2[0] - sign * NODE_HALF_W, p2[1])
        return start, end
    sign = 1 if dy >= ZERO_DELTA else -1
    start = (p1[0], p1[1] + sign * NODE_HALF_H)
    end = (p2[0], p2[1] - sign * NODE_HALF_H)
    return start, end


def _draw_arrowhead(
    draw: ImageDraw.ImageDraw,
    start: Point,
    end: Point,
) -> None:
    """Рисует наконечник стрелки в точке end."""
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    left = (
        int(end[0] - ARROW_LEN * math.cos(angle - ARROW_ANGLE)),
        int(end[1] - ARROW_LEN * math.sin(angle - ARROW_ANGLE)),
    )
    right = (
        int(end[0] - ARROW_LEN * math.cos(angle + ARROW_ANGLE)),
        int(end[1] - ARROW_LEN * math.sin(angle + ARROW_ANGLE)),
    )
    draw.polygon([end, left, right], fill=EDGE_COLOR)


def _draw_node(
    draw: ImageDraw.ImageDraw,
    font: ImageFont.ImageFont,
    name: str,
    center: Point,
) -> None:
    """Рисует прямоугольник узла и подпись пакета."""
    cx, cy = center
    box = (
        cx - NODE_HALF_W,
        cy - NODE_HALF_H,
        cx + NODE_HALF_W,
        cy + NODE_HALF_H,
    )
    draw.rectangle(box, fill=BOX_FILL, outline=BOX_BORDER, width=LINE_WIDTH)
    bbox = draw.textbbox((0, 0), name, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((cx - tw // 2, cy - th // 2), name, fill=TEXT_COLOR, font=font)
