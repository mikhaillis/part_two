# Визуализация графа зависимостей

Вариант 9. Этап 4: обратные зависимости (DFS с рекурсией).

Репозиторий: https://github.com/mikhaillis/part_two

## 1. Общее описание

CLI-инструмент для построения и визуализации графа зависимостей
менеджера пакетов Ubuntu (apt). Реализованы разбор параметров,
загрузка индекса Packages **по URL**, построение транзитивного графа
алгоритмом DFS с рекурсией, ограничение глубины, фильтрация по
подстроке и обработка циклов. В тестовом режиме вместо URL указывается
путь к файлу описания графа, где пакеты названы большими латинскими
буквами. Режим `--reverse` выводит обратные зависимости — пакеты,
которые зависят от заданного; для обхода используется тот же DFS.
Готовые менеджеры пакетов и библиотеки для получения зависимостей
не используются.

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
| `--reverse` | Вывести обратные зависимости (кто зависит от пакета) |

Без `--test-mode` параметр `--repo` обязан быть URL (`http://` /
`https://`). При запуске печатаются рёбра графа: `пакет -> зависимость`.
В режиме `--reverse` рёбра печатаются в том же направлении, но обход
идёт от заданного пакета к зависящим от него пакетам.

Модули `src/`:

| Модуль | Назначение |
|---|---|
| `config.py` | Разбор и проверка параметров CLI |
| `apt_repo.py` | Загрузка и разбор индекса Packages |
| `graph.py` | Прямой граф зависимостей, DFS с рекурсией |
| `reverse.py` | Обращение графа и обход обратных зависимостей |
| `main.py` | Точка входа, выбор режима |

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
test_stage4.bat
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
./test_stage4.sh
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

Обратные зависимости пакета `D` (`tests/graph_reverse.txt`):

```text
python src/main.py --package D --repo tests/graph_reverse.txt \
  --test-mode --pkg-version 1 --output graph.png --max-depth 5 --reverse

B -> D
A -> B
C -> D
A -> C
E -> D
F -> E
```

Обратные зависимости `curl` по URL (`--max-depth 2`):

```text
ec2-instance-connect -> curl
pollinate -> curl
ubuntu-server -> pollinate
...
```

Если от пакета никто не зависит, выводится `обратных зависимостей нет`.

Ошибки:

```text
ошибка: без --test-mode --repo должен быть URL (http:// или https://)
ошибка: не удалось загрузить репозиторий: ...
ошибка: пакет не найден: nosuchpkg
```
