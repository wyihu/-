#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "[install] backend deps (python)"
if command -v uv >/dev/null 2>&1; then
  (cd backend && uv pip install -e .)
else
  (cd backend && python3 -m pip install -e .)
fi

echo "[install] done"
