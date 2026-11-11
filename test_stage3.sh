#!/usr/bin/env sh
set -e

REPO="http://archive.ubuntu.com/ubuntu/dists/jammy/main/binary-amd64/Packages.gz"
VER="7.81.0-1"

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
echo "=== Stage 3: apt graph from repository URL ==="
python3 src/main.py --package curl --repo "$REPO" \
  --pkg-version "$VER" --output graph.png --max-depth 2

echo
echo "=== Stage 3: apt graph with filter ==="
python3 src/main.py --package curl --repo "$REPO" \
  --pkg-version "$VER" --output graph.png --max-depth 2 --filter ssl

echo
echo "=== Stage 3: unknown root ==="
if python3 src/main.py --package Z --repo tests/graph_simple.txt \
  --test-mode --pkg-version 1 --output graph.png --max-depth 2; then
  echo "expected error" >&2
  exit 1
fi

echo
echo "=== Stage 3 passed ==="
