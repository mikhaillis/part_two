"""Точка входа CLI визуализации графа зависимостей (вариант 9)."""

from __future__ import annotations

import sys

from apt_repo import get_direct_dependencies, load_repository
from config import EXIT_ERROR, EXIT_OK, load_config


def main(argv: list[str] | None = None) -> int:
    """
    Загружает параметры, читает индекс apt и печатает
    прямые зависимости выбранного пакета.

    Returns:
        Код завершения процесса.
    """
    try:
        config = load_config(argv)
        index = load_repository(config.repo, config.test_mode)
        deps = get_direct_dependencies(
            index,
            config.package,
            config.pkg_version,
        )
    except ValueError as err:
        print(f"ошибка: {err}", file=sys.stderr)
        return EXIT_ERROR

    for name in deps:
        print(name)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
