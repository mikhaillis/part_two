@echo off
chcp 65001 > nul
python src\main.py --package curl --repo tests\sample_repo.txt --test-mode --pkg-version 7.68.0 --output graph.png --max-depth 3 --filter lib
