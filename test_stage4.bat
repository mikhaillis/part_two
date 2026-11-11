@echo off
chcp 65001 > nul
setlocal
set JAMMY=http://archive.ubuntu.com/ubuntu/dists/jammy/main/binary-amd64/Packages.gz
set NOBLE=http://archive.ubuntu.com/ubuntu/dists/noble/main/binary-amd64/Packages.gz
set COMMON=--test-mode --pkg-version 1 --output graph.png --reverse
set REAL=--output graph.png --reverse

echo ##### Test repository #####
echo.
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
echo === Stage 4: unknown root ===
python src\main.py --package Z --repo tests\graph_reverse.txt %COMMON% --max-depth 2
if not errorlevel 1 (
  echo expected error
  exit /b 1
)

echo.
echo ##### Real repository: Ubuntu 22.04 jammy main #####
echo.
echo === Stage 4: jammy curl, depth 2 ===
python src\main.py --package curl --repo %JAMMY% --pkg-version 7.81.0-1 %REAL% --max-depth 2
if errorlevel 1 exit /b 1

echo.
echo === Stage 4: jammy libcurl4, depth 1 ===
python src\main.py --package libcurl4 --repo %JAMMY% --pkg-version 7.81.0-1 %REAL% --max-depth 1
if errorlevel 1 exit /b 1

echo.
echo === Stage 4: jammy libjq1, depth 3 (transitive) ===
python src\main.py --package libjq1 --repo %JAMMY% --pkg-version 1.6-2.1ubuntu3 %REAL% --max-depth 3
if errorlevel 1 exit /b 1

echo.
echo === Stage 4: jammy openssh-client, depth 2, filter python ===
python src\main.py --package openssh-client --repo %JAMMY% --pkg-version 1:8.9p1-3 %REAL% --max-depth 2 --filter python
if errorlevel 1 exit /b 1

echo.
echo === Stage 4: jammy nano, no dependents ===
python src\main.py --package nano --repo %JAMMY% --pkg-version 6.2-1 %REAL% --max-depth 2
if errorlevel 1 exit /b 1

echo.
echo === Stage 4: jammy curl, missing version ===
python src\main.py --package curl --repo %JAMMY% --pkg-version 9.9.9 %REAL% --max-depth 2
if not errorlevel 1 (
  echo expected error
  exit /b 1
)

echo.
echo === Stage 4: jammy unknown package ===
python src\main.py --package nosuchpkg --repo %JAMMY% --pkg-version 1.0 %REAL% --max-depth 2
if not errorlevel 1 (
  echo expected error
  exit /b 1
)

echo.
echo ##### Real repository: Ubuntu 24.04 noble main #####
echo.
echo === Stage 4: noble curl, depth 2 ===
python src\main.py --package curl --repo %NOBLE% --pkg-version 8.5.0-2ubuntu10 %REAL% --max-depth 2
if errorlevel 1 exit /b 1

echo.
echo === Stage 4: noble wget, depth 1 ===
python src\main.py --package wget --repo %NOBLE% --pkg-version 1.21.4-1ubuntu4 %REAL% --max-depth 1
if errorlevel 1 exit /b 1

echo.
echo === Stage 4 passed ===
endlocal
