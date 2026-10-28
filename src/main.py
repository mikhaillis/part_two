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


def main(argv: list[str] | None = None) -> int:
    """
    Загружает параметры и печатает граф зависимостей.

    Returns:
        Код завершения процесса.
    """
    try:
        config = load_config(argv)
        edges = _build_edges(config)
    except ValueError as err:
        print(f"ошибка: {err}", file=sys.stderr)
        return EXIT_ERROR

    text = format_edges(edges)
    if text:
        print(text)
    return EXIT_OK


def _build_edges(config: AppConfig) -> list[tuple[str, str]]:
    """Строит рёбра графа в тестовом или apt-режиме."""
    if config.test_mode:
        adjacency = load_test_graph(config.repo)
        return build_graph_from_test(
            adjacency,
            config.package,
            config.max_depth,
            config.filter,
        )
    index = load_repository(config.repo, test_mode=False)
    return build_graph_from_apt(
        index,
        config.package,
        config.pkg_version,
        config.max_depth,
        config.filter,
    )


if __name__ == "__main__":
    sys.exit(main())
