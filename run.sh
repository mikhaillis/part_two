#!/usr/bin/env sh
python3 src/main.py --package curl --repo tests/sample_packages.txt \
  --test-mode --pkg-version 7.68.0 --output graph.png --max-depth 3 \
  --filter lib
