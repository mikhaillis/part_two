@echo off
chcp 65001 > nul
setlocal

echo === Stage 2: direct deps ===
python src\main.py --package curl --repo tests\sample_packages.txt --test-mode --pkg-version 7.68.0 --output graph.png --max-depth 3 --filter lib
if errorlevel 1 exit /b 1

echo.
echo === Stage 2: missing version ===
python src\main.py --package curl --repo tests\sample_packages.txt --test-mode --pkg-version 9.9.9 --output graph.png --max-depth 3
if not errorlevel 1 (
  echo expected error
  exit /b 1
)

echo.
echo === Stage 2: unknown package ===
python src\main.py --package nosuchpkg --repo tests\sample_packages.txt --test-mode --pkg-version 1.0 --output graph.png --max-depth 2
if not errorlevel 1 (
  echo expected error
  exit /b 1
)

echo.
echo === Stage 2: nested package deps ===
python src\main.py --package libcurl4 --repo tests\sample_packages.txt --test-mode --pkg-version 7.68.0 --output graph.png --max-depth 2
if errorlevel 1 exit /b 1

echo.
echo === Stage 2 passed ===
endlocal
