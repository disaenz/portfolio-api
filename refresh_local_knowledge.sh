#!/bin/sh
set -eu

cd "$(dirname "$0")"

if ! docker compose ps --status running --services | grep -qx api; then
  echo "The local stack is not running. Start it first with ./run_dev.sh" >&2
  exit 1
fi

docker compose exec api python scripts/refresh_portfolio_knowledge.py
