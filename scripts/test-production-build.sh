#!/usr/bin/env bash
set -Eeuo pipefail

IMAGE="rap-production-test:local"

docker build -t "${IMAGE}" .
docker run --rm \
    -e DJANGO_SETTINGS_MODULE=rap.settings_test \
    -e DJANGO_SECRET_KEY=test-only-not-used-in-production-000000000000000000 \
    -e DATABASE_URL=sqlite:///:memory: \
    -e EMAIL_BACKEND=django.core.mail.backends.locmem.EmailBackend \
    "${IMAGE}" \
    python manage.py check --settings=rap.settings_test
docker run --rm \
    -e DJANGO_SETTINGS_MODULE=rap.settings_test \
    -e DJANGO_SECRET_KEY=test-only-not-used-in-production-000000000000000000 \
    -e DATABASE_URL=sqlite:///:memory: \
    -e EMAIL_BACKEND=django.core.mail.backends.locmem.EmailBackend \
    "${IMAGE}" \
    python manage.py test --settings=rap.settings_test --noinput

echo "[OK] Build e suite completa validados sem PostgreSQL ou SMTP de producao"
