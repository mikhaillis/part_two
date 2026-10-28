@echo off
chcp 65001 > nul
setlocal

echo === Stage 2: direct deps via apt index file ===
python src\main.py --package curl --repo tests\sample_packages.txt --pkg-version 7.68.0 --output graph.png --max-depth 1
if errorlevel 1 exit /b 1

echo.
echo === Stage 2: missing version ===
python src\main.py --package curl --repo tests\sample_packages.txt --pkg-version 9.9.9 --output graph.png --max-depth 1
if not errorlevel 1 (
  echo expected error
  exit /b 1
)

echo.
echo === Stage 2: unknown package ===
python src\main.py --package nosuchpkg --repo tests\sample_packages.txt --pkg-version 1.0 --output graph.png --max-depth 1
if not errorlevel 1 (
  echo expected error
  exit /b 1
)

echo.
echo === Stage 2: nested package ===
python src\main.py --package libcurl4 --repo tests\sample_packages.txt --pkg-version 7.68.0 --output graph.png --max-depth 1
if errorlevel 1 exit /b 1

echo.
echo === Stage 2 passed ===
endlocal
