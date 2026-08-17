#!/usr/bin/env bash
# بوابة القبول: ruff ثم pytest. أي إخفاق يغلق البوابة.
set -uo pipefail
cd "$(dirname "$0")"

if command -v ruff >/dev/null 2>&1; then RUFF="ruff"; else RUFF="python -m ruff"; fi
if command -v pytest >/dev/null 2>&1; then PYTEST="pytest"; else PYTEST="python -m pytest"; fi

fail=0

echo "── ruff check"
$RUFF check . || fail=1

echo "── pytest"
$PYTEST -q || fail=1

echo
if [ "$fail" -ne 0 ]; then
  echo "✗ البوابة مغلقة"
  exit 1
fi
echo "✓ البوابة مفتوحة"
