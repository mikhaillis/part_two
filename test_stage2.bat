@echo off
chcp 65001 > nul
setlocal
set REPO=http://archive.ubuntu.com/ubuntu/dists/jammy/main/binary-amd64/Packages.gz
set VER=7.81.0-1

echo === Stage 2: direct deps via apt URL ===
python src\main.py --package curl --repo %REPO% --pkg-version %VER% --output graph.png --max-depth 1
if errorlevel 1 exit /b 1

echo.
echo === Stage 2: missing version ===
python src\main.py --package curl --repo %REPO% --pkg-version 9.9.9 --output graph.png --max-depth 1
if not errorlevel 1 (
  echo expected error
  exit /b 1
)

echo.
echo === Stage 2: unknown package ===
python src\main.py --package nosuchpkg --repo %REPO% --pkg-version 1.0 --output graph.png --max-depth 1
if not errorlevel 1 (
  echo expected error
  exit /b 1
)

echo.
echo === Stage 2: local path rejected without test-mode ===
python src\main.py --package curl --repo tests\graph_simple.txt --pkg-version %VER% --output graph.png --max-depth 1
if not errorlevel 1 (
  echo expected error
  exit /b 1
)

echo.
echo === Stage 2 passed ===
endlocal
