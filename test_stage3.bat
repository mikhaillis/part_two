@echo off
chcp 65001 > nul
setlocal
set REPO=http://archive.ubuntu.com/ubuntu/dists/jammy/main/binary-amd64/Packages.gz
set VER=7.81.0-1

echo === Stage 3: simple graph ===
python src\main.py --package A --repo tests\graph_simple.txt --test-mode --pkg-version 1 --output graph.png --max-depth 3
if errorlevel 1 exit /b 1

echo.
echo === Stage 3: depth limit ===
python src\main.py --package A --repo tests\graph_deep.txt --test-mode --pkg-version 1 --output graph.png --max-depth 2
if errorlevel 1 exit /b 1

echo.
echo === Stage 3: cycle ===
python src\main.py --package A --repo tests\graph_cycle.txt --test-mode --pkg-version 1 --output graph.png --max-depth 5
if errorlevel 1 exit /b 1

echo.
echo === Stage 3: filter substring ===
python src\main.py --package A --repo tests\graph_simple.txt --test-mode --pkg-version 1 --output graph.png --max-depth 3 --filter B
if errorlevel 1 exit /b 1

echo.
echo === Stage 3: apt graph from repository URL ===
python src\main.py --package curl --repo %REPO% --pkg-version %VER% --output graph.png --max-depth 2
if errorlevel 1 exit /b 1

echo.
echo === Stage 3: apt graph with filter ===
python src\main.py --package curl --repo %REPO% --pkg-version %VER% --output graph.png --max-depth 2 --filter ssl
if errorlevel 1 exit /b 1

echo.
echo === Stage 3: unknown root ===
python src\main.py --package Z --repo tests\graph_simple.txt --test-mode --pkg-version 1 --output graph.png --max-depth 2
if not errorlevel 1 (
  echo expected error
  exit /b 1
)

echo.
echo === Stage 3 passed ===
endlocal
