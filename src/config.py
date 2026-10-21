"""Разбор и проверка параметров командной строки (этап 1)."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from pathlib import Path

MIN_DEPTH = 1
EXIT_OK = 0
EXIT_ERROR = 1

PARAM_ORDER = (
    "package",
    "repo",
    "test_mode",
    "pkg_version",
    "output",
    "max_depth",
    "filter",
)


@dataclass(frozen=True)
class AppConfig:
    """Настройки приложения, задаваемые пользователем."""

    package: str
    repo: str
    test_mode: bool
    pkg_version: str
    output: str
    max_depth: int
    filter: str


def _add_str_option(
    parser: argparse.ArgumentParser,
    name: str,
    help_text: str,
    default: str | None = None,
) -> None:
    """Добавляет строковый аргумент командной строки."""
    kwargs: dict = {"type": str, "help": help_text}
    if default is not None:
        kwargs["default"] = default
    parser.add_argument(name, **kwargs)


def build_parser() -> argparse.ArgumentParser:
    """Создаёт парсер опций командной строки."""
    parser = argparse.ArgumentParser(
        description="Визуализация графа зависимостей (вариант 9)",
    )
    _add_str_option(parser, "--package", "Имя анализируемого пакета")
    _add_str_option(
        parser,
        "--repo",
        "URL репозитория или путь к тестовому файлу",
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Режим работы с тестовым репозиторием",
    )
    _add_str_option(parser, "--pkg-version", "Версия пакета")
    _add_str_option(
        parser,
        "--output",
        "Имя сгенерированного файла изображения графа",
    )
    _add_str_option(
        parser,
        "--max-depth",
        "Максимальная глубина анализа зависимостей",
    )
    _add_str_option(
        parser,
        "--filter",
        "Подстрока для фильтрации пакетов",
        default="",
    )
    return parser


def _require_text(value: str | None, label: str) -> str:
    """Проверяет, что строковый параметр задан и не пуст."""
    if value is None or not value.strip():
        raise ValueError(f"не указан параметр {label}")
    return value.strip()


def _parse_max_depth(raw: str | None) -> int:
    """Проверяет и преобразует максимальную глубину."""
    if raw is None or not str(raw).strip():
        raise ValueError(
            "не указана максимальная глубина (--max-depth)"
        )
    try:
        depth = int(str(raw).strip())
    except ValueError as err:
        raise ValueError(
            "максимальная глубина должна быть целым числом"
        ) from err
    if depth < MIN_DEPTH:
        raise ValueError(
            f"максимальная глубина должна быть >= {MIN_DEPTH}"
        )
    return depth


def _validate_repo(repo: str, test_mode: bool) -> str:
    """Проверяет путь/URL репозитория с учётом режима теста."""
    if test_mode:
        path = Path(repo)
        if not path.is_file():
            raise ValueError(
                "в режиме теста --repo должен указывать "
                "на существующий файл"
            )
        return str(path)
    if not repo:
        raise ValueError("не указан адрес репозитория (--repo)")
    return repo


def _validate_output(name: str) -> str:
    """Проверяет имя выходного файла изображения."""
    path = Path(name)
    if path.name == "" or path.name in {".", ".."}:
        raise ValueError("некорректное имя файла (--output)")
    if path.suffix == "":
        raise ValueError(
            "имя файла изображения должно содержать расширение"
        )
    return name


def validate_config(args: argparse.Namespace) -> AppConfig:
    """
    Проверяет все параметры пользователя.

    Raises:
        ValueError: если любой параметр задан неверно.
    """
    package = _require_text(args.package, "имя пакета (--package)")
    repo_raw = _require_text(args.repo, "адрес репозитория (--repo)")
    pkg_version = _require_text(
        args.pkg_version,
        "версия пакета (--pkg-version)",
    )
    output_raw = _require_text(
        args.output,
        "имя файла изображения (--output)",
    )

    test_mode = bool(args.test_mode)
    repo = _validate_repo(repo_raw, test_mode)
    output = _validate_output(output_raw)
    max_depth = _parse_max_depth(args.max_depth)
    filter_value = args.filter if args.filter is not None else ""

    return AppConfig(
        package=package,
        repo=repo,
        test_mode=test_mode,
        pkg_version=pkg_version,
        output=output,
        max_depth=max_depth,
        filter=filter_value,
    )


def format_config(config: AppConfig) -> str:
    """Форматирует параметры в виде ключ = значение."""
    data = asdict(config)
    lines = [f"{key} = {data[key]}" for key in PARAM_ORDER]
    return "\n".join(lines)


def load_config(argv: list[str] | None = None) -> AppConfig:
    """Читает аргументы CLI и возвращает проверенную конфигурацию."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return validate_config(args)
