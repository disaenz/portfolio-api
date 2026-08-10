#!/bin/sh
set -eu

export PGPASSWORD="${POSTGRES_PASSWORD}"

until pg_isready -h "${POSTGRES_HOST:-db}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}"; do
  sleep 1
done

psql -v ON_ERROR_STOP=1 -h "${POSTGRES_HOST:-db}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -f /migrations/schema.sql

psql -v ON_ERROR_STOP=1 -h "${POSTGRES_HOST:-db}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -f /migrations/mock_data.sql
