#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -f .env ]; then
  echo "Creating .env from .env.example ..."
  cp .env.example .env
  echo "Edit .env before production use (especially DJANGO_SECRET_KEY)."
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed."
  exit 1
fi

docker compose up -d --build

echo ""
echo "Deploy finished (isolated docker-panel stack)."
echo "Host Docker containers are NOT managed by this panel."
echo "Panel listens on 127.0.0.1:${HTTP_PORT:-8080} (host port 80 is NOT used)."
echo "Add deploy/host-nginx.server.it-zone.uz.conf to your existing nginx for the domain."
echo "Test: curl http://127.0.0.1:${HTTP_PORT:-8080}/api/health/"
