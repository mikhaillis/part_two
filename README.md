# Визуализация графа зависимостей

Вариант 9. Этап 3: построение графа зависимостей (DFS с рекурсией).

Репозиторий: https://github.com/mikhaillis/part_two

## 1. Общее описание

CLI-инструмент для построения и визуализации графа зависимостей
менеджера пакетов Ubuntu (apt). Реализованы разбор параметров,
загрузка индекса Packages **по URL**, построение транзитивного графа
алгоритмом DFS с рекурсией, ограничение глубины, фильтрация по
подстроке и обработка циклов. В тестовом режиме вместо URL указывается
путь к файлу описания графа, где пакеты названы большими латинскими
буквами. Готовые менеджеры пакетов и библиотеки для получения
зависимостей не используются.

## 2. Описание функций и настроек

Параметры командной строки:

| Параметр | Описание |
|---|---|
| `--package` | Имя анализируемого пакета |
| `--repo` | URL индекса Packages **или** путь к тестовому файлу |
| `--test-mode` | Тестовый репозиторий (файл графа `A -> B`) |
| `--pkg-version` | Версия пакета (для apt) |
| `--output` | Имя файла изображения графа |
| `--max-depth` | Максимальная глубина анализа (>= 1) |
| `--filter` | Подстрока: такие пакеты не учитываются |

Без `--test-mode` параметр `--repo` обязан быть URL (`http://` /
`https://`). При запуске печатаются рёбра графа: `пакет -> зависимость`.

## 3. Сборка и запуск тестов

```bat
set REPO=http://archive.ubuntu.com/ubuntu/dists/jammy/main/binary-amd64/Packages.gz

python src\main.py --package curl --repo %REPO% ^
  --pkg-version 7.81.0-1 --output graph.png --max-depth 2

python src\main.py --package A --repo tests\graph_simple.txt ^
  --test-mode --pkg-version 1 --output graph.png --max-depth 3

run.bat
test_stage1.bat
test_stage2.bat
test_stage3.bat
```

```sh
REPO="http://archive.ubuntu.com/ubuntu/dists/jammy/main/binary-amd64/Packages.gz"

python3 src/main.py --package curl --repo "$REPO" \
  --pkg-version 7.81.0-1 --output graph.png --max-depth 2

python3 src/main.py --package A --repo tests/graph_simple.txt \
  --test-mode --pkg-version 1 --output graph.png --max-depth 3

./run.sh
./test_stage1.sh
./test_stage2.sh
./test_stage3.sh
```

## 4. Примеры использования

Граф по URL (apt, без `--test-mode`):

```text
curl -> libc6
curl -> libcurl4
curl -> zlib1g
...
```

Тестовый граф (`--test-mode`):

```text
A -> B
A -> C
B -> D
C -> D
```

Ограничение глубины, циклы и `--filter` поддерживаются в обоих режимах.

Ошибки:

```text
ошибка: без --test-mode --repo должен быть URL (http:// или https://)
ошибка: не удалось загрузить репозиторий: ...
ошибка: пакет не найден: nosuchpkg
```
