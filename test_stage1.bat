@echo off
chcp 65001 > nul
setlocal

echo === Stage 1: success ===
python src\main.py --package A --repo tests\sample_repo.txt --test-mode --pkg-version 1 --output graph.png --max-depth 3 --filter lib
if errorlevel 1 exit /b 1

echo.
echo === Stage 1: missing package ===
python src\main.py --repo tests\sample_repo.txt --test-mode --pkg-version 1 --output graph.png --max-depth 3
if not errorlevel 1 (
  echo expected error
  exit /b 1
)

echo.
echo === Stage 1: bad depth ===
python src\main.py --package A --repo tests\sample_repo.txt --test-mode --pkg-version 1 --output graph.png --max-depth 0
if not errorlevel 1 (
  echo expected error
  exit /b 1
)

echo.
echo === Stage 1: missing test file ===
python src\main.py --package A --repo missing.txt --test-mode --pkg-version 1 --output graph.png --max-depth 2
if not errorlevel 1 (
  echo expected error
  exit /b 1
)

echo.
echo === Stage 1: output without extension ===
python src\main.py --package A --repo tests\sample_repo.txt --test-mode --pkg-version 1 --output graph --max-depth 2
if not errorlevel 1 (
  echo expected error
  exit /b 1
)

echo.
echo === Stage 1 passed ===
endlocal
