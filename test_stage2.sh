#!/usr/bin/env sh
set -e

REPO="http://archive.ubuntu.com/ubuntu/dists/jammy/main/binary-amd64/Packages.gz"
VER="7.81.0-1"

echo "=== Stage 2: direct deps via apt URL ==="
python3 src/main.py --package curl --repo "$REPO" \
  --pkg-version "$VER" --output graph.png --max-depth 1

echo
echo "=== Stage 2: missing version ==="
if python3 src/main.py --package curl --repo "$REPO" \
  --pkg-version 9.9.9 --output graph.png --max-depth 1; then
  echo "expected error" >&2
  exit 1
fi

echo
echo "=== Stage 2: unknown package ==="
if python3 src/main.py --package nosuchpkg --repo "$REPO" \
  --pkg-version 1.0 --output graph.png --max-depth 1; then
  echo "expected error" >&2
  exit 1
fi

echo
echo "=== Stage 2: local path rejected without test-mode ==="
if python3 src/main.py --package curl --repo tests/graph_simple.txt \
  --pkg-version "$VER" --output graph.png --max-depth 1; then
  echo "expected error" >&2
  exit 1
fi

echo
echo "=== Stage 2 passed ==="
