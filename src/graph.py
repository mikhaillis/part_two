"""Построение графа зависимостей алгоритмом DFS с рекурсией."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from apt_repo import PackageIndex, get_direct_dependencies, parse_depends

NeighborsFn = Callable[[str], list[str]]

EDGE_ARROW = "->"
COMMENT_PREFIX = "#"
ROOT_DEPTH = 0


def parse_test_graph(text: str) -> dict[str, list[str]]:
    """
    Разбирает тестовый граф вида «A -> B».

    Имена пакетов — большие латинские буквы (допускаются
    и более длинные идентификаторы из латиницы).
    """
    adjacency: dict[str, list[str]] = {}
    for raw_line in text.splitlines():
        _absorb_test_line(adjacency, raw_line)
    return adjacency


def _absorb_test_line(
    adjacency: dict[str, list[str]],
    raw_line: str,
) -> None:
    """Добавляет одно ребро из строки тестового файла."""
    line = raw_line.strip()
    if not line or line.startswith(COMMENT_PREFIX):
        return
    if EDGE_ARROW not in line:
        raise ValueError(f"неверный формат ребра: {raw_line}")
    left, right = line.split(EDGE_ARROW, 1)
    src = left.strip()
    dst = right.strip()
    if not src or not dst:
        raise ValueError(f"неверный формат ребра: {raw_line}")
    _append_unique(adjacency, src, dst)
    adjacency.setdefault(dst, [])


def _append_unique(
    adjacency: dict[str, list[str]],
    src: str,
    dst: str,
) -> None:
    """Добавляет зависимость, избегая дубликатов."""
    deps = adjacency.setdefault(src, [])
    if dst not in deps:
        deps.append(dst)


def load_test_graph(path: str) -> dict[str, list[str]]:
    """Загружает тестовый граф из файла."""
    text = Path(path).read_text(encoding="utf-8")
    graph = parse_test_graph(text)
    if not graph:
        raise ValueError("тестовый граф пуст или имеет неверный формат")
    return graph


def _should_skip(name: str, name_filter: str) -> bool:
    """Проверяет, нужно ли исключить пакет по подстроке."""
    if not name_filter:
        return False
    return name_filter in name


def _deps_from_index(index: PackageIndex, name: str) -> list[str]:
    """Возвращает прямые зависимости первой доступной версии."""
    versions = index.versions_of(name)
    if not versions:
        return []
    return get_direct_dependencies(index, name, versions[0])


def _deps_from_record(
    index: PackageIndex,
    name: str,
    version: str,
) -> list[str]:
    """Возвращает прямые зависимости конкретной версии."""
    record = index.get(name, version)
    if record is None:
        return _deps_from_index(index, name)
    return parse_depends(record.depends)


class GraphBuilder:
    """Строит множество рёбер графа зависимостей через DFS."""

    def __init__(
        self,
        max_depth: int,
        name_filter: str,
        neighbors: NeighborsFn,
    ) -> None:
        """Сохраняет ограничения обхода и функцию соседей."""
        self._max_depth = max_depth
        self._filter = name_filter
        self._neighbors = neighbors
        self._edges: list[tuple[str, str]] = []
        self._visiting: set[str] = set()
        self._expanded: set[str] = set()

    def build(self, root: str) -> list[tuple[str, str]]:
        """Запускает DFS от корневого пакета и возвращает рёбра."""
        self._edges = []
        self._visiting = set()
        self._expanded = set()
        self._dfs(root, ROOT_DEPTH)
        return list(self._edges)

    def _dfs(self, name: str, depth: int) -> None:
        """Рекурсивный обход зависимостей с учётом циклов."""
        if depth >= self._max_depth:
            return
        if name in self._visiting:
            return
        if name in self._expanded:
            return
        self._visiting.add(name)
        for dep in self._neighbors(name):
            self._visit_dep(name, dep, depth)
        self._visiting.remove(name)
        self._expanded.add(name)

    def _visit_dep(self, src: str, dep: str, depth: int) -> None:
        """Добавляет ребро и продолжает обход, если нужно."""
        if _should_skip(dep, self._filter):
            return
        edge = (src, dep)
        if edge not in self._edges:
            self._edges.append(edge)
        self._dfs(dep, depth + 1)


def build_graph_from_test(
    adjacency: dict[str, list[str]],
    root: str,
    max_depth: int,
    name_filter: str,
) -> list[tuple[str, str]]:
    """Строит граф по тестовой матрице смежности."""
    if root not in adjacency:
        raise ValueError(f"пакет не найден в тестовом графе: {root}")

    def neighbors(name: str) -> list[str]:
        return list(adjacency.get(name, []))

    builder = GraphBuilder(max_depth, name_filter, neighbors)
    return builder.build(root)


def build_graph_from_apt(
    index: PackageIndex,
    root: str,
    version: str,
    max_depth: int,
    name_filter: str,
) -> list[tuple[str, str]]:
    """Строит граф по индексу apt для заданной версии корня."""
    if index.get(root, version) is None:
        known = index.versions_of(root)
        if not known:
            raise ValueError(f"пакет не найден: {root}")
        raise ValueError(
            f"версия {version} пакета {root} не найдена "
            f"(доступны: {', '.join(known)})"
        )

    def neighbors(name: str) -> list[str]:
        if name == root:
            return _deps_from_record(index, name, version)
        return _deps_from_index(index, name)

    builder = GraphBuilder(max_depth, name_filter, neighbors)
    return builder.build(root)


def format_edges(edges: list[tuple[str, str]]) -> str:
    """Форматирует рёбра графа для вывода на экран."""
    lines = [f"{src} {EDGE_ARROW} {dst}" for src, dst in edges]
    return "\n".join(lines)
