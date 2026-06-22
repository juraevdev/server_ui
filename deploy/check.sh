#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PORT="${HTTP_PORT:-8080}"
if [ -f .env ]; then
  # shellcheck disable=SC2046
  export $(grep -E '^HTTP_PORT=' .env | xargs) 2>/dev/null || true
  PORT="${HTTP_PORT:-8080}"
fi

echo "=== docker compose ps ==="
docker compose ps

echo ""
echo "=== curl panel (127.0.0.1:${PORT}) ==="
curl -sv "http://127.0.0.1:${PORT}/api/health/" 2>&1 | tail -20 || true

echo ""
echo "=== backend logs (last 30) ==="
docker compose logs --tail=30 backend 2>/dev/null || true

echo ""
echo "=== frontend logs (last 30) ==="
docker compose logs --tail=30 frontend 2>/dev/null || true

echo ""
echo "=== nginx logs (last 20) ==="
docker compose logs --tail=20 nginx 2>/dev/null || true
