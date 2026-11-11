"""Обратные зависимости: какие пакеты зависят от заданного (этап 4)."""

from __future__ import annotations

from apt_repo import PackageIndex, parse_depends, require_record
from graph import GraphBuilder

Adjacency = dict[str, list[str]]
Edge = tuple[str, str]


def _append_unique(adjacency: Adjacency, src: str, dst: str) -> None:
    """Добавляет ребро src -> dst, избегая дубликатов."""
    targets = adjacency.setdefault(src, [])
    if dst not in targets:
        targets.append(dst)


def invert_adjacency(adjacency: Adjacency) -> Adjacency:
    """
    Обращает граф: для каждой зависимости собирает зависящих от неё.

    Ребро «A зависит от B» превращается в ребро «B -> A».
    """
    inverted: Adjacency = {}
    for package, deps in adjacency.items():
        inverted.setdefault(package, [])
        for dep in deps:
            _append_unique(inverted, dep, package)
    return inverted


def reverse_adjacency_from_index(index: PackageIndex) -> Adjacency:
    """Строит обратный граф по всем записям индекса apt."""
    inverted: Adjacency = {}
    for record in index.records():
        inverted.setdefault(record.name, [])
        for dep in parse_depends(record.depends):
            _append_unique(inverted, dep, record.name)
    return inverted


def _traverse(
    inverted: Adjacency,
    root: str,
    max_depth: int,
    name_filter: str,
) -> list[Edge]:
    """Обходит обратный граф тем же DFS, что и на этапе 3."""

    def neighbors(name: str) -> list[str]:
        """Возвращает пакеты, напрямую зависящие от name."""
        return list(inverted.get(name, []))

    builder = GraphBuilder(max_depth, name_filter, neighbors)
    return builder.build(root)


def build_reverse_from_test(
    adjacency: Adjacency,
    root: str,
    max_depth: int,
    name_filter: str,
) -> list[Edge]:
    """Возвращает рёбра обратных зависимостей в тестовом графе."""
    if root not in adjacency:
        raise ValueError(f"пакет не найден в тестовом графе: {root}")
    inverted = invert_adjacency(adjacency)
    return _traverse(inverted, root, max_depth, name_filter)


def build_reverse_from_apt(
    index: PackageIndex,
    root: str,
    version: str,
    max_depth: int,
    name_filter: str,
) -> list[Edge]:
    """Возвращает рёбра обратных зависимостей по индексу apt."""
    require_record(index, root, version)
    inverted = reverse_adjacency_from_index(index)
    return _traverse(inverted, root, max_depth, name_filter)


def flip_edges(edges: list[Edge]) -> list[Edge]:
    """Разворачивает рёбра обратно в направление «пакет -> зависимость»."""
    return [(dst, src) for src, dst in edges]
