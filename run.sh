#!/usr/bin/env sh
python3 src/main.py --package A --repo tests/graph_simple.txt \
  --test-mode --pkg-version 1 --output graph.png --max-depth 3
