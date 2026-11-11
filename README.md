# Визуализация графа зависимостей

Вариант 9. Этап 5: визуализация графа зависимостей (D2 и PNG).

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
На этапе 5 формируется описание графа на языке диаграмм **D2**
(сохраняется в `.d2`) и изображение графа в формате **PNG**.
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
| `--output` | Имя выходного PNG-файла изображения графа (`.png`) |
| `--max-depth` | Максимальная глубина анализа (>= 1) |
| `--filter` | Подстрока: такие пакеты не учитываются |
| `--reverse` | Вывести обратные зависимости (кто зависит от пакета) |

Без `--test-mode` параметр `--repo` обязан быть URL (`http://` /
`https://`). При запуске печатаются рёбра графа (`пакет -> зависимость`),
рядом с выходным файлом `--output` сохраняется D2-диаграмма (`.d2`)
и рендерится изображение графа в формате `.png` (через утилиту `d2`,
а при её отсутствии — встроенным рендерером).

Модули `src/`:

| Модуль | Назначение |
|---|---|
| `config.py` | Разбор и проверка параметров CLI |
| `apt_repo.py` | Загрузка и разбор индекса Packages |
| `graph.py` | Прямой граф зависимостей, DFS с рекурсией |
| `reverse.py` | Обращение графа и обход обратных зависимостей |
| `visualize.py` | Генерация D2-диаграммы и сохранение PNG |
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
test_stage5.bat
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
./test_stage5.sh
```

## 4. Примеры использования и визуализации (3 пакета)

### Пакет 1: `jq` (`1.6-2.1ubuntu3`, Ubuntu 22.04 jammy, глубина 2)

```sh
python src/main.py --package jq --repo "$JAMMY" \
  --pkg-version 1.6-2.1ubuntu3 --output out_jq.png --max-depth 2
```

Сгенерированный D2 (`out_jq.d2`):

```d2
"jq" -> "libjq1"
"libjq1" -> "libc6"
"libjq1" -> "libonig5"
"jq" -> "libc6"
"libc6" -> "libgcc-s1"
"libc6" -> "libcrypt1"
```

### Пакет 2: `nano` (`6.2-1`, Ubuntu 22.04 jammy, глубина 2)

```sh
python src/main.py --package nano --repo "$JAMMY" \
  --pkg-version 6.2-1 --output out_nano.png --max-depth 2
```

Сгенерированный D2 (`out_nano.d2`):

```d2
"nano" -> "libc6"
"libc6" -> "libgcc-s1"
"libc6" -> "libcrypt1"
"nano" -> "libncursesw6"
"libncursesw6" -> "libtinfo6"
"libncursesw6" -> "libc6"
"nano" -> "libtinfo6"
"libtinfo6" -> "libc6"
```

### Пакет 3: `curl` (`8.5.0-2ubuntu10`, Ubuntu 24.04 noble, глубина 2)

```sh
python src/main.py --package curl --repo "$NOBLE" \
  --pkg-version 8.5.0-2ubuntu10 --output out_curl.png --max-depth 2
```

Фрагмент D2 (`out_curl.d2`):

```d2
"curl" -> "libc6"
"libc6" -> "libgcc-s1"
"curl" -> "libcurl4t64"
"libcurl4t64" -> "libbrotli1"
"libcurl4t64" -> "libc6"
"libcurl4t64" -> "libgssapi-krb5-2"
...
"curl" -> "zlib1g"
"zlib1g" -> "libc6"
```

### Обратные зависимости (`--reverse`)

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

Если от пакета никто не зависит, выводится `обратных зависимостей нет`.

## 5. Сравнение со штатными инструментами apt (`apt-cache` / `debtree`)

Штатные средства визуализации и анализа зависимостей в Ubuntu/Debian —
`apt-cache dotty <pkg>`, `apt-cache depends --recurse <pkg>` и `debtree <pkg>`.
При сравнении наших графов (`jq`, `nano`, `curl`) с их выводом возможны
следующие расхождения и их причины:

1. **Только поле `Depends`:** наш инструмент разбирает строго поле
   `Depends` выбранного файла `Packages.gz`, тогда как `apt-cache depends`
   и `debtree` по умолчанию дополнительно включают `Pre-Depends`,
   `Recommends` и `Suggests` (например, у `curl` появляется `ca-certificates`
   через `Recommends`).
2. **Один срез индекса (`main`) против всех подключённых источников:**
   мы анализируем конкретный URL индекса (например, `jammy/main`),
   а `apt-cache` объединяет `main`, `updates`, `security`, `universe`
   и локальный `/var/lib/dpkg/status`, поэтому версии и транзитивные
   зависимости пакетов, обновлённых в `jammy-updates`/`jammy-security`,
   могут отличаться.
3. **Альтернативные зависимости (`A | B`) и виртуальные пакеты:**
   наш парсер включает все пакеты из OR-группы `Depends` и ищет точное
   совпадение `Package`, тогда как `apt`/`debtree` выбирают приоритетную
   альтернативу и разрешают виртуальные пакеты через поле `Provides`.
4. **Ограничение глубины и фильтрация:** наш инструмент поддерживает
   `--max-depth` и `--filter`, а `apt-cache dotty` строит полный граф
   до базовых пакетов системы (`libgcc-s1`, `gcc-12-base`, ` debconf`).
