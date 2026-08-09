#!/bin/sh
set -eu

cd "$(dirname "$0")"

if [ -z "${PSQL_URL:-}" ] && [ -f .env ]; then
  PSQL_URL=$(sed -n 's/^PSQL_URL=//p' .env | tail -n 1)
  PSQL_URL=${PSQL_URL#\"}
  PSQL_URL=${PSQL_URL%\"}
  PSQL_URL=${PSQL_URL#\'}
  PSQL_URL=${PSQL_URL%\'}
fi

if [ -z "${PSQL_URL:-}" ]; then
  echo "PSQL_URL is required. Add it to .env or export it before running this script." >&2
  exit 1
fi

if ! command -v psql >/dev/null 2>&1; then
  echo "psql is required. Install the PostgreSQL client and try again." >&2
  exit 1
fi

exec psql "$PSQL_URL"
