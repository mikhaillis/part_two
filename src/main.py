"""Точка входа CLI визуализации графа зависимостей (вариант 9)."""

from __future__ import annotations

import sys

from config import EXIT_ERROR, EXIT_OK, format_config, load_config


def main(argv: list[str] | None = None) -> int:
    """
    Загружает параметры и печатает их в формате ключ = значение.

    Returns:
        Код завершения процесса.
    """
    try:
        config = load_config(argv)
    except ValueError as err:
        print(f"ошибка: {err}", file=sys.stderr)
        return EXIT_ERROR

    print(format_config(config))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
