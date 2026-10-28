"""Загрузка и разбор индекса пакетов apt (формат Packages)."""

from __future__ import annotations

import gzip
import urllib.error
import urllib.request
from pathlib import Path

FIELD_PACKAGE = "Package"
FIELD_VERSION = "Version"
FIELD_DEPENDS = "Depends"
DEP_SEPARATOR = ","
ALT_SEPARATOR = "|"
CONTINUATION_PREFIX = " "
PARAGRAPH_SEPARATOR = "\n\n"
HTTP_TIMEOUT_SEC = 60
GZ_SUFFIX = ".gz"
EMPTY = ""
GZIP_HEADER_LEN = 2
GZIP_MAGIC_0 = 0x1F
GZIP_MAGIC_1 = 0x8B


class PackageRecord:
    """Описание одного пакета из индекса apt."""

    def __init__(self, name: str, version: str, depends: str) -> None:
        """Сохраняет имя, версию и сырое поле Depends."""
        self.name = name
        self.version = version
        self.depends = depends


class PackageIndex:
    """Индекс пакетов, доступный по имени и версии."""

    def __init__(self) -> None:
        """Создаёт пустой индекс."""
        self._by_key: dict[tuple[str, str], PackageRecord] = {}

    def add(self, record: PackageRecord) -> None:
        """Добавляет запись пакета в индекс."""
        key = (record.name, record.version)
        self._by_key[key] = record

    def get(self, name: str, version: str) -> PackageRecord | None:
        """Возвращает пакет по имени и версии или None."""
        return self._by_key.get((name, version))

    def versions_of(self, name: str) -> list[str]:
        """Возвращает известные версии пакета."""
        return [ver for (pkg, ver) in self._by_key if pkg == name]

    def is_empty(self) -> bool:
        """Проверяет, что индекс не содержит пакетов."""
        return not self._by_key


def _read_url_bytes(url: str) -> bytes:
    """Скачивает содержимое URL как байты."""
    try:
        with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT_SEC) as resp:
            return resp.read()
    except urllib.error.URLError as err:
        raise ValueError(f"не удалось загрузить репозиторий: {err}") from err


def _decode_packages_bytes(data: bytes, source: str) -> str:
    """Декодирует Packages, при необходимости распаковывая gzip."""
    if source.endswith(GZ_SUFFIX) or _looks_like_gzip(data):
        try:
            data = gzip.decompress(data)
        except OSError as err:
            raise ValueError("некорректный gzip-архив Packages") from err
    return data.decode("utf-8", errors="replace")


def _looks_like_gzip(data: bytes) -> bool:
    """Проверяет сигнатуру gzip (1F 8B)."""
    if len(data) < GZIP_HEADER_LEN:
        return False
    return data[0] == GZIP_MAGIC_0 and data[1] == GZIP_MAGIC_1


def _read_local_text(path: Path) -> str:
    """Читает локальный файл индекса Packages."""
    raw = path.read_bytes()
    return _decode_packages_bytes(raw, path.name)


def _split_paragraphs(text: str) -> list[str]:
    """Делит текст Packages на параграфы пакетов."""
    normalized = text.replace("\r\n", "\n").strip()
    if not normalized:
        return []
    parts = normalized.split(PARAGRAPH_SEPARATOR)
    return [part.strip() for part in parts if part.strip()]


def _parse_fields(paragraph: str) -> dict[str, str]:
    """Разбирает поля одного параграфа Debian-контроля."""
    fields: dict[str, str] = {}
    current_key = EMPTY
    for line in paragraph.split("\n"):
        current_key = _absorb_line(fields, current_key, line)
    return fields


def _absorb_line(
    fields: dict[str, str],
    current_key: str,
    line: str,
) -> str:
    """Добавляет строку в словарь полей и возвращает текущий ключ."""
    if line.startswith(CONTINUATION_PREFIX) and current_key:
        fields[current_key] += "\n" + line[1:]
        return current_key
    if ":" not in line:
        return current_key
    key, value = line.split(":", 1)
    key = key.strip()
    fields[key] = value.strip()
    return key


def _record_from_fields(fields: dict[str, str]) -> PackageRecord | None:
    """Создаёт запись пакета из словаря полей."""
    name = fields.get(FIELD_PACKAGE, EMPTY).strip()
    version = fields.get(FIELD_VERSION, EMPTY).strip()
    if not name or not version:
        return None
    depends = fields.get(FIELD_DEPENDS, EMPTY).strip()
    return PackageRecord(name=name, version=version, depends=depends)


def parse_packages_text(text: str) -> PackageIndex:
    """Строит индекс пакетов из текста формата Packages."""
    index = PackageIndex()
    for paragraph in _split_paragraphs(text):
        record = _record_from_fields(_parse_fields(paragraph))
        if record is not None:
            index.add(record)
    return index


def load_repository(repo: str, test_mode: bool) -> PackageIndex:
    """
    Загружает индекс пакетов из файла или по URL.

    Raises:
        ValueError: если источник недоступен или пуст.
    """
    if test_mode:
        text = _read_local_text(Path(repo))
    else:
        raw = _read_url_bytes(repo)
        text = _decode_packages_bytes(raw, repo)
    index = parse_packages_text(text)
    if index.is_empty():
        raise ValueError("индекс пакетов пуст или имеет неверный формат")
    return index


def _strip_version_constraint(token: str) -> str:
    """Убирает ограничение версии и архитектуру из токена Depends."""
    cleaned = token.strip()
    if "(" in cleaned:
        cleaned = cleaned.split("(", 1)[0].strip()
    if ":" in cleaned:
        cleaned = cleaned.split(":", 1)[0].strip()
    return cleaned


def parse_depends(raw: str) -> list[str]:
    """Извлекает имена прямых зависимостей из поля Depends."""
    if not raw.strip():
        return []
    names: list[str] = []
    seen: set[str] = set()
    for group in raw.split(DEP_SEPARATOR):
        _add_group_names(group, names, seen)
    return names


def _add_group_names(
    group: str,
    names: list[str],
    seen: set[str],
) -> None:
    """Добавляет имена пакетов из OR-группы Depends."""
    for alt in group.split(ALT_SEPARATOR):
        name = _strip_version_constraint(alt)
        if name and name not in seen:
            seen.add(name)
            names.append(name)


def get_direct_dependencies(
    index: PackageIndex,
    name: str,
    version: str,
) -> list[str]:
    """
    Возвращает прямые зависимости пакета указанной версии.

    Raises:
        ValueError: если пакет или версия не найдены.
    """
    record = index.get(name, version)
    if record is None:
        known = index.versions_of(name)
        if not known:
            raise ValueError(f"пакет не найден: {name}")
        raise ValueError(
            f"версия {version} пакета {name} не найдена "
            f"(доступны: {', '.join(known)})"
        )
    return parse_depends(record.depends)
