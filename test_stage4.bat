@echo off
chcp 65001 > nul
setlocal
set REPO=http://archive.ubuntu.com/ubuntu/dists/jammy/main/binary-amd64/Packages.gz
set VER=7.81.0-1
set COMMON=--test-mode --pkg-version 1 --output graph.png --reverse

echo === Stage 4: reverse deps of D ===
python src\main.py --package D --repo tests\graph_reverse.txt %COMMON% --max-depth 5
if errorlevel 1 exit /b 1

echo.
echo === Stage 4: reverse deps with depth limit ===
python src\main.py --package D --repo tests\graph_reverse.txt %COMMON% --max-depth 1
if errorlevel 1 exit /b 1

echo.
echo === Stage 4: reverse deps with filter ===
python src\main.py --package D --repo tests\graph_reverse.txt %COMMON% --max-depth 5 --filter E
if errorlevel 1 exit /b 1

echo.
echo === Stage 4: reverse deps in cycle ===
python src\main.py --package A --repo tests\graph_cycle.txt %COMMON% --max-depth 5
if errorlevel 1 exit /b 1

echo.
echo === Stage 4: package without dependents ===
python src\main.py --package A --repo tests\graph_reverse.txt %COMMON% --max-depth 5
if errorlevel 1 exit /b 1

echo.
echo === Stage 4: reverse deps from apt URL ===
python src\main.py --package curl --repo %REPO% --pkg-version %VER% --output graph.png --max-depth 2 --reverse
if errorlevel 1 exit /b 1

echo.
echo === Stage 4: unknown root ===
python src\main.py --package Z --repo tests\graph_reverse.txt %COMMON% --max-depth 2
if not errorlevel 1 (
  echo expected error
  exit /b 1
)

echo.
echo === Stage 4 passed ===
endlocal
