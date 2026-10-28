# Визуализация графа зависимостей

Вариант 9. Этап 2: сбор прямых зависимостей пакетов Ubuntu (apt).

## 1. Общее описание

CLI-инструмент для построения и визуализации графа зависимостей
менеджера пакетов Ubuntu (apt). На данном этапе реализованы разбор
параметров командной строки, загрузка индекса Packages (файл или URL)
и вывод прямых зависимостей заданной версии пакета. Готовые менеджеры
пакетов и библиотеки для получения зависимостей не используются.

## 2. Описание функций и настроек

Параметры командной строки:

| Параметр | Описание |
|---|---|
| `--package` | Имя анализируемого пакета |
| `--repo` | URL индекса Packages или путь к тестовому файлу |
| `--test-mode` | Режим работы с тестовым репозиторием (локальный файл) |
| `--pkg-version` | Версия пакета |
| `--output` | Имя файла изображения графа |
| `--max-depth` | Максимальная глубина анализа (>= 1) |
| `--filter` | Подстрока для фильтрации пакетов |

При запуске приложение печатает прямые зависимости пакета
(по одной на строку).

## 3. Сборка и запуск тестов

```bat
python src\main.py --package curl --repo tests\sample_packages.txt ^
  --test-mode --pkg-version 7.68.0 --output graph.png --max-depth 3 ^
  --filter lib

run.bat
test_stage1.bat
test_stage2.bat
```

```sh
python3 src/main.py --package curl --repo tests/sample_packages.txt \
  --test-mode --pkg-version 7.68.0 --output graph.png --max-depth 3 \
  --filter lib

./run.sh
./test_stage1.sh
./test_stage2.sh
```

Пример с URL индекса Ubuntu (без `--test-mode`):

```bat
python src\main.py --package curl ^
  --repo http://archive.ubuntu.com/ubuntu/dists/jammy/main/binary-amd64/Packages.gz ^
  --pkg-version 7.81.0-1 --output graph.png --max-depth 2
```

## 4. Примеры использования

Успешный запуск (тестовый индекс):

```text
libc6
libcurl4
zlib1g
```

Ошибки:

```text
ошибка: пакет не найден: nosuchpkg
ошибка: версия 9.9.9 пакета curl не найдена (доступны: 7.68.0)
ошибка: индекс пакетов пуст или имеет неверный формат
```
