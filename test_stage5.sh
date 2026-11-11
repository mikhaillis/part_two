#!/usr/bin/env sh
set -e

JAMMY="http://archive.ubuntu.com/ubuntu/dists/jammy/main/binary-amd64/Packages.gz"
NOBLE="http://archive.ubuntu.com/ubuntu/dists/noble/main/binary-amd64/Packages.gz"

cleanup() {
  rm -f out_simple.png out_simple.d2 \
    out_jq.png out_jq.d2 \
    out_nano.png out_nano.d2 \
    out_curl.png out_curl.d2
}
trap cleanup EXIT

echo "##### Stage 5: Test graph visualization (D2 + PNG) #####"
echo
echo "=== Test case 1: simple graph ==="
python3 src/main.py --package A --repo tests/graph_simple.txt \
  --test-mode --pkg-version 1 --output out_simple.png --max-depth 3
test -s out_simple.png
test -s out_simple.d2
echo "--- D2 source (out_simple.d2) ---"
cat out_simple.d2

echo
echo "##### Stage 5: 3 real packages visualization (D2 + PNG) #####"
echo
echo "=== Package 1: jq (Ubuntu 22.04 jammy, depth 2) ==="
python3 src/main.py --package jq --repo "$JAMMY" \
  --pkg-version 1.6-2.1ubuntu3 --output out_jq.png --max-depth 2
test -s out_jq.png
test -s out_jq.d2
echo "--- D2 source (out_jq.d2) ---"
cat out_jq.d2

echo
echo "=== Package 2: nano (Ubuntu 22.04 jammy, depth 2) ==="
python3 src/main.py --package nano --repo "$JAMMY" \
  --pkg-version 6.2-1 --output out_nano.png --max-depth 2
test -s out_nano.png
test -s out_nano.d2
echo "--- D2 source (out_nano.d2) ---"
cat out_nano.d2

echo
echo "=== Package 3: curl (Ubuntu 24.04 noble, depth 2) ==="
python3 src/main.py --package curl --repo "$NOBLE" \
  --pkg-version 8.5.0-2ubuntu10 --output out_curl.png --max-depth 2
test -s out_curl.png
test -s out_curl.d2
echo "--- D2 source (out_curl.d2) ---"
cat out_curl.d2

echo
echo "=== Error check: non-PNG output extension rejected ==="
if python3 src/main.py --package A --repo tests/graph_simple.txt \
  --test-mode --pkg-version 1 --output graph.svg --max-depth 2; then
  echo "expected error" >&2
  exit 1
fi

echo
echo "=== Stage 5 passed ==="
