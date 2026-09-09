#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="/home/web/Sites/rap/public"
COMPOSE_FILE="${PROJECT_DIR}/docker-compose.yml"
EXPECTED_DB_VOLUME="public_pgdata"
ENV_STATE_DIR="/home/gabrielnatalnet/.rap-deploy"
ENV_STATE_FILE="${ENV_STATE_DIR}/web-env.sha256"
COMPOSE=(docker-compose -p public -f "${COMPOSE_FILE}")

fail() {
    echo "[ERRO] $*" >&2
    exit 1
}

[[ -d "${PROJECT_DIR}" && -f "${COMPOSE_FILE}" ]] || fail "Projeto canonico nao encontrado"
[[ -f "${PROJECT_DIR}/.env" ]] || fail ".env de producao nao encontrado"
cd "${PROJECT_DIR}"

docker --version
compose_version=$(docker-compose version --short 2>/dev/null || docker-compose --version)
echo "[INFO] docker-compose: ${compose_version}"
if [[ "${compose_version}" == 1.29.2* ]]; then
    echo "[AVISO] Compose v1.29.2 pode falhar com KeyError: ContainerConfig no Docker Engine atual."
    echo "[AVISO] Sera usado o fluxo compativel, sem --force-recreate."
fi
"${COMPOSE[@]}" config -q || fail "docker-compose.yml invalido"

db_id=$("${COMPOSE[@]}" ps -q db)
[[ -n "${db_id}" ]] || fail "Servico db do projeto public nao encontrado"
db_running=$(docker inspect --format '{{.State.Running}}' "${db_id}")
db_health=$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}sem-healthcheck{{end}}' "${db_id}")
db_project=$(docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "${db_id}")
db_service=$(docker inspect --format '{{index .Config.Labels "com.docker.compose.service"}}' "${db_id}")
db_volume=$(docker inspect --format '{{range .Mounts}}{{if eq .Destination "/var/lib/postgresql/data"}}{{.Type}}:{{.Name}}{{end}}{{end}}' "${db_id}")

[[ "${db_running}" == "true" && "${db_health}" == "healthy" ]] || fail "PostgreSQL nao esta saudavel"
[[ "${db_project}" == "public" && "${db_service}" == "db" ]] || fail "DB pertence a outro projeto/servico"
[[ "${db_volume}" == "volume:${EXPECTED_DB_VOLUME}" ]] || fail "Volume DB inesperado: ${db_volume:-nenhum}"
echo "[OK] PostgreSQL saudavel"
echo "[OK] Volume de producao: ${EXPECTED_DB_VOLUME}"
echo "[OK] Banco protegido; somente o web sera recriado"

echo "[INFO] Validando a configuracao atual antes de parar o web"
"${COMPOSE[@]}" run --rm --no-deps -T web python manage.py check
"${COMPOSE[@]}" run --rm --no-deps -T web python manage.py makemigrations --check --dry-run

web_id=$("${COMPOSE[@]}" ps -q web)
if [[ -n "${web_id}" ]]; then
    web_project=$(docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "${web_id}")
    web_service=$(docker inspect --format '{{index .Config.Labels "com.docker.compose.service"}}' "${web_id}")
    [[ "${web_project}" == "public" && "${web_service}" == "web" ]] || fail "Container alvo nao e o web do projeto public"

    echo "[INFO] Parando exclusivamente o servico web"
    "${COMPOSE[@]}" stop web
    echo "[INFO] Removendo exclusivamente o container web, sem remover volumes"
    docker rm "${web_id}"
fi

echo "[INFO] Criando somente o web, sem dependencias e sem build"
"${COMPOSE[@]}" up -d --no-deps --no-build web

new_web_id=$("${COMPOSE[@]}" ps -q web)
[[ -n "${new_web_id}" ]] || fail "Novo container web nao foi criado"
echo "[INFO] Aguardando healthcheck do novo web (ate 120 segundos)"
for _ in $(seq 1 24); do
    running=$(docker inspect --format '{{.State.Running}}' "${new_web_id}")
    health=$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}sem-healthcheck{{end}}' "${new_web_id}")
    if [[ "${running}" == "true" && "${health}" == "healthy" ]]; then
        break
    fi
    sleep 5
done

running=$(docker inspect --format '{{.State.Running}}' "${new_web_id}")
health=$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}sem-healthcheck{{end}}' "${new_web_id}")
if [[ "${running}" != "true" || "${health}" != "healthy" ]]; then
    "${COMPOSE[@]}" logs --tail=30 web >&2 || true
    fail "Novo web nao ficou saudavel: running=${running} health=${health}"
fi

docker exec "${new_web_id}" python -c \
    "import urllib.request; r=urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8000/health/', headers={'Host':'rap.natalnet.br','X-Forwarded-Proto':'https'}), timeout=5); assert r.status == 200"

umask 077
mkdir -p "${ENV_STATE_DIR}"
sha256sum "${PROJECT_DIR}/.env" | awk '{print $1}' >"${ENV_STATE_FILE}"
echo "[OK] Novo web saudavel e referencia segura do .env atualizada"
echo "[SUCESSO] Somente o servico web foi recriado; db e volumes permaneceram intactos"
