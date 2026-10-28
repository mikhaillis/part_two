#!/usr/bin/env sh
set -e

echo "=== Stage 2: direct deps via apt index file ==="
python3 src/main.py --package curl --repo tests/sample_packages.txt \
  --pkg-version 7.68.0 --output graph.png --max-depth 1

echo
echo "=== Stage 2: missing version ==="
if python3 src/main.py --package curl --repo tests/sample_packages.txt \
  --pkg-version 9.9.9 --output graph.png --max-depth 1; then
  echo "expected error" >&2
  exit 1
fi

echo
echo "=== Stage 2: unknown package ==="
if python3 src/main.py --package nosuchpkg --repo tests/sample_packages.txt \
  --pkg-version 1.0 --output graph.png --max-depth 1; then
  echo "expected error" >&2
  exit 1
fi

echo
echo "=== Stage 2: nested package ==="
python3 src/main.py --package libcurl4 --repo tests/sample_packages.txt \
  --pkg-version 7.68.0 --output graph.png --max-depth 1

echo
echo "=== Stage 2 passed ==="
