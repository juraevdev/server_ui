#!/bin/sh
set -e

python manage.py migrate --noinput

exec gunicorn server_ui.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 2 \
  --timeout 300 \
  --access-logfile - \
  --error-logfile -
