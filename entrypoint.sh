#!/usr/bin/env bash
set -e

echo "Aplicando migrações..."
python manage.py migrate --noinput

echo "Coletando estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando Gunicorn..."
exec gunicorn rap.wsgi:application --bind 0.0.0.0:8000 --workers 3
