#!/usr/bin/env sh
set -e

echo "=== Stage 1: success ==="
python3 src/main.py --package A --repo tests/sample_repo.txt \
  --test-mode --pkg-version 1 --output graph.png --max-depth 3 \
  --filter lib

echo
echo "=== Stage 1: missing package ==="
if python3 src/main.py --repo tests/sample_repo.txt --test-mode \
  --pkg-version 1 --output graph.png --max-depth 3; then
  echo "expected error" >&2
  exit 1
fi

echo
echo "=== Stage 1: bad depth ==="
if python3 src/main.py --package A --repo tests/sample_repo.txt \
  --test-mode --pkg-version 1 --output graph.png --max-depth 0; then
  echo "expected error" >&2
  exit 1
fi

echo
echo "=== Stage 1: missing test file ==="
if python3 src/main.py --package A --repo missing.txt --test-mode \
  --pkg-version 1 --output graph.png --max-depth 2; then
  echo "expected error" >&2
  exit 1
fi

echo
echo "=== Stage 1: output without extension ==="
if python3 src/main.py --package A --repo tests/sample_repo.txt \
  --test-mode --pkg-version 1 --output graph --max-depth 2; then
  echo "expected error" >&2
  exit 1
fi

echo
echo "=== Stage 1 passed ==="
