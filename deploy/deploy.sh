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
echo "Open: http://YOUR_SERVER_IP"
echo "Health: http://YOUR_SERVER_IP/api/health/"
