#!/bin/sh
set -eu

cd "$(dirname "$0")"
docker compose up --build --detach "$@"

echo "Portfolio stack is running in the background."
echo "Site: http://localhost:5173"
echo "API:  http://localhost:8010/docs"
echo "Logs: docker compose logs -f"
echo "PostgreSQL: docker compose exec db psql -U portfolio -d portfolio_local"
