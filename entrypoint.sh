#!/usr/bin/env bash
set -Eeuo pipefail

echo "Iniciando Gunicorn..."
exec gunicorn rap.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --timeout "${GUNICORN_TIMEOUT:-60}" \
    --access-logfile - \
    --error-logfile -
