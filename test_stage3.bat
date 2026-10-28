@echo off
chcp 65001 > nul
setlocal

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
echo === Stage 3: apt graph from local Packages ===
python src\main.py --package curl --repo tests\sample_packages.txt --pkg-version 7.68.0 --output graph.png --max-depth 2
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
