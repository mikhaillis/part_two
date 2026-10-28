@echo off
chcp 65001 > nul
python src\main.py --package A --repo tests\graph_simple.txt --test-mode --pkg-version 1 --output graph.png --max-depth 3
