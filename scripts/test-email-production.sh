#!/usr/bin/env bash
set -Eeuo pipefail

if [[ $# -ne 1 || ! "${1}" =~ ^[A-Za-z0-9.!#$%\&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
    echo "Uso: $0 endereco@teste.com" >&2
    exit 2
fi

PROJECT_DIR="/home/web/Sites/rap/public"
COMPOSE=(docker-compose -p public -f "${PROJECT_DIR}/docker-compose.yml")
recipient="$1"

echo "Este comando MANUAL enviara um unico e-mail SMTP para: ${recipient}"
"${COMPOSE[@]}" run --rm --no-deps -T -e RAP_TEST_RECIPIENT="${recipient}" web \
    python manage.py shell -c \
    "import os; from django.core.mail import send_mail; from django.conf import settings; n=send_mail('Teste manual SMTP - RAP','Este e um teste manual do SMTP do RAP.',settings.DEFAULT_FROM_EMAIL,[os.environ['RAP_TEST_RECIPIENT']],fail_silently=False); assert n == 1"
echo "[OK] O servidor SMTP aceitou o e-mail de teste"
