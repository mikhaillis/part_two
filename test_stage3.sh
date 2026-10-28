#!/usr/bin/env sh
set -e

echo "=== Stage 3: simple graph ==="
python3 src/main.py --package A --repo tests/graph_simple.txt \
  --test-mode --pkg-version 1 --output graph.png --max-depth 3

echo
echo "=== Stage 3: depth limit ==="
python3 src/main.py --package A --repo tests/graph_deep.txt \
  --test-mode --pkg-version 1 --output graph.png --max-depth 2

echo
echo "=== Stage 3: cycle ==="
python3 src/main.py --package A --repo tests/graph_cycle.txt \
  --test-mode --pkg-version 1 --output graph.png --max-depth 5

echo
echo "=== Stage 3: filter substring ==="
python3 src/main.py --package A --repo tests/graph_simple.txt \
  --test-mode --pkg-version 1 --output graph.png --max-depth 3 --filter B

echo
echo "=== Stage 3: apt graph from local Packages ==="
python3 src/main.py --package curl --repo tests/sample_packages.txt \
  --pkg-version 7.68.0 --output graph.png --max-depth 2

echo
echo "=== Stage 3: unknown root ==="
if python3 src/main.py --package Z --repo tests/graph_simple.txt \
  --test-mode --pkg-version 1 --output graph.png --max-depth 2; then
  echo "expected error" >&2
  exit 1
fi

echo
echo "=== Stage 3 passed ==="
