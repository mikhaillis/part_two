#!/usr/bin/env sh
set -e

JAMMY="http://archive.ubuntu.com/ubuntu/dists/jammy/main/binary-amd64/Packages.gz"
NOBLE="http://archive.ubuntu.com/ubuntu/dists/noble/main/binary-amd64/Packages.gz"

run_test() {
  python3 src/main.py --test-mode --pkg-version 1 --output graph.png \
    --reverse "$@"
}

run_real() {
  python3 src/main.py --output graph.png --reverse "$@"
}

expect_fail() {
  if "$@"; then
    echo "expected error" >&2
    exit 1
  fi
}

echo "##### Test repository #####"
echo
echo "=== Stage 4: reverse deps of D ==="
run_test --package D --repo tests/graph_reverse.txt --max-depth 5

echo
echo "=== Stage 4: reverse deps with depth limit ==="
run_test --package D --repo tests/graph_reverse.txt --max-depth 1

echo
echo "=== Stage 4: reverse deps with filter ==="
run_test --package D --repo tests/graph_reverse.txt --max-depth 5 \
  --filter E

echo
echo "=== Stage 4: reverse deps in cycle ==="
run_test --package A --repo tests/graph_cycle.txt --max-depth 5

echo
echo "=== Stage 4: package without dependents ==="
run_test --package A --repo tests/graph_reverse.txt --max-depth 5

echo
echo "=== Stage 4: unknown root ==="
expect_fail run_test --package Z --repo tests/graph_reverse.txt \
  --max-depth 2

echo
echo "##### Real repository: Ubuntu 22.04 jammy main #####"
echo
echo "=== Stage 4: jammy curl, depth 2 ==="
run_real --package curl --repo "$JAMMY" --pkg-version 7.81.0-1 \
  --max-depth 2

echo
echo "=== Stage 4: jammy libcurl4, depth 1 ==="
run_real --package libcurl4 --repo "$JAMMY" --pkg-version 7.81.0-1 \
  --max-depth 1

echo
echo "=== Stage 4: jammy libjq1, depth 3 (transitive) ==="
run_real --package libjq1 --repo "$JAMMY" \
  --pkg-version 1.6-2.1ubuntu3 --max-depth 3

echo
echo "=== Stage 4: jammy openssh-client, depth 2, filter python ==="
run_real --package openssh-client --repo "$JAMMY" \
  --pkg-version 1:8.9p1-3 --max-depth 2 --filter python

echo
echo "=== Stage 4: jammy nano, no dependents ==="
run_real --package nano --repo "$JAMMY" --pkg-version 6.2-1 \
  --max-depth 2

echo
echo "=== Stage 4: jammy curl, missing version ==="
expect_fail run_real --package curl --repo "$JAMMY" \
  --pkg-version 9.9.9 --max-depth 2

echo
echo "=== Stage 4: jammy unknown package ==="
expect_fail run_real --package nosuchpkg --repo "$JAMMY" \
  --pkg-version 1.0 --max-depth 2

echo
echo "##### Real repository: Ubuntu 24.04 noble main #####"
echo
echo "=== Stage 4: noble curl, depth 2 ==="
run_real --package curl --repo "$NOBLE" \
  --pkg-version 8.5.0-2ubuntu10 --max-depth 2

echo
echo "=== Stage 4: noble wget, depth 1 ==="
run_real --package wget --repo "$NOBLE" \
  --pkg-version 1.21.4-1ubuntu4 --max-depth 1

echo
echo "=== Stage 4 passed ==="
