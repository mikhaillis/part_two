#!/usr/bin/env sh
set -e

REPO="http://archive.ubuntu.com/ubuntu/dists/jammy/main/binary-amd64/Packages.gz"
VER="7.81.0-1"

echo "=== Stage 4: reverse deps of D ==="
python3 src/main.py --package D --repo tests/graph_reverse.txt \
  --test-mode --pkg-version 1 --output graph.png --max-depth 5 --reverse

echo
echo "=== Stage 4: reverse deps with depth limit ==="
python3 src/main.py --package D --repo tests/graph_reverse.txt \
  --test-mode --pkg-version 1 --output graph.png --max-depth 1 --reverse

echo
echo "=== Stage 4: reverse deps with filter ==="
python3 src/main.py --package D --repo tests/graph_reverse.txt \
  --test-mode --pkg-version 1 --output graph.png --max-depth 5 \
  --filter E --reverse

echo
echo "=== Stage 4: reverse deps in cycle ==="
python3 src/main.py --package A --repo tests/graph_cycle.txt \
  --test-mode --pkg-version 1 --output graph.png --max-depth 5 --reverse

echo
echo "=== Stage 4: package without dependents ==="
python3 src/main.py --package A --repo tests/graph_reverse.txt \
  --test-mode --pkg-version 1 --output graph.png --max-depth 5 --reverse

echo
echo "=== Stage 4: reverse deps from apt URL ==="
python3 src/main.py --package curl --repo "$REPO" \
  --pkg-version "$VER" --output graph.png --max-depth 2 --reverse

echo
echo "=== Stage 4: unknown root ==="
if python3 src/main.py --package Z --repo tests/graph_reverse.txt \
  --test-mode --pkg-version 1 --output graph.png --max-depth 2 --reverse
then
  echo "expected error" >&2
  exit 1
fi

echo
echo "=== Stage 4 passed ==="
