"""Точка входа CLI визуализации графа зависимостей (вариант 9)."""

from __future__ import annotations

import sys

from apt_repo import load_repository
from config import EXIT_ERROR, EXIT_OK, AppConfig, load_config
from graph import (
    build_graph_from_apt,
    build_graph_from_test,
    format_edges,
    load_test_graph,
)
from reverse import (
    build_reverse_from_apt,
    build_reverse_from_test,
    flip_edges,
)
from visualize import render_png

Edge = tuple[str, str]
NO_REVERSE_DEPS = "обратных зависимостей нет"


def main(argv: list[str] | None = None) -> int:
    """
    Загружает параметры, строит граф и сохраняет его в PNG (D2).

    Returns:
        Код завершения процесса.
    """
    try:
        config = load_config(argv)
        edges = _build_edges(config)
        render_png(edges, config.package, config.output)
    except ValueError as err:
        print(f"ошибка: {err}", file=sys.stderr)
        return EXIT_ERROR

    text = format_edges(edges)
    if text:
        print(text)
    elif config.reverse:
        print(NO_REVERSE_DEPS)
    return EXIT_OK


def _build_edges(config: AppConfig) -> list[Edge]:
    """Выбирает режим: прямые или обратные зависимости."""
    if config.reverse:
        return flip_edges(_build_reverse(config))
    return _build_direct(config)


def _build_direct(config: AppConfig) -> list[Edge]:
    """Строит рёбра графа в тестовом или apt-режиме."""
    if config.test_mode:
        adjacency = load_test_graph(config.repo)
        return build_graph_from_test(
            adjacency,
            config.package,
            config.max_depth,
            config.filter,
        )
    index = load_repository(config.repo)
    return build_graph_from_apt(
        index,
        config.package,
        config.pkg_version,
        config.max_depth,
        config.filter,
    )


def _build_reverse(config: AppConfig) -> list[Edge]:
    """Строит рёбра обратных зависимостей (зависимый <- пакет)."""
    if config.test_mode:
        adjacency = load_test_graph(config.repo)
        return build_reverse_from_test(
            adjacency,
            config.package,
            config.max_depth,
            config.filter,
        )
    index = load_repository(config.repo)
    return build_reverse_from_apt(
        index,
        config.package,
        config.pkg_version,
        config.max_depth,
        config.filter,
    )


if __name__ == "__main__":
    sys.exit(main())
