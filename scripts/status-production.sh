#!/usr/bin/env bash
set -u

PROJECT_DIR="/home/web/Sites/rap/public"
COMPOSE=(docker-compose -p public -f "${PROJECT_DIR}/docker-compose.yml")

echo "Containers do projeto public:"
"${COMPOSE[@]}" ps

db_id=$("${COMPOSE[@]}" ps -q db 2>/dev/null || true)
if [[ -n "${db_id}" ]]; then
    docker inspect --format 'db: status={{.State.Status}} health={{if .State.Health}}{{.State.Health.Status}}{{else}}sem-healthcheck{{end}} restart={{.HostConfig.RestartPolicy.Name}}' "${db_id}"
    docker inspect --format 'db volume: {{range .Mounts}}{{if eq .Destination "/var/lib/postgresql/data"}}type={{.Type}} name={{.Name}} destination={{.Destination}}{{end}}{{end}}' "${db_id}"
else
    echo "db: nao encontrado"
fi

web_id=$("${COMPOSE[@]}" ps -q web 2>/dev/null || true)
if [[ -n "${web_id}" ]]; then
    docker inspect --format 'web: status={{.State.Status}} health={{if .State.Health}}{{.State.Health.Status}}{{else}}sem-healthcheck{{end}} restart={{.HostConfig.RestartPolicy.Name}}' "${web_id}"
    echo "Porta publicada pelo web:"
    docker port "${web_id}" 8000/tcp 2>/dev/null || echo "porta 8000 nao publicada"
    echo "Resposta interna de /health/:"
    docker exec "${web_id}" python -c \
        "import urllib.request; r=urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8000/health/', headers={'Host':'rap.natalnet.br','X-Forwarded-Proto':'https'}), timeout=5); print('HTTP', r.status, r.read().decode())" \
        2>&1 || echo "healthcheck HTTP falhou"
else
    echo "web: nao encontrado"
fi

echo "Ultimas 30 linhas dos logs web:"
"${COMPOSE[@]}" logs --tail=30 web 2>&1 || true
