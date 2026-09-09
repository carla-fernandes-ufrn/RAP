#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="/home/web/Sites/rap/public"
COMPOSE_FILE="${PROJECT_DIR}/docker-compose.yml"
EXPECTED_DB_VOLUME="public_pgdata"
BACKUP_DIR="/home/gabrielnatalnet/rap-backups"
COMPOSE=(docker-compose -p public -f "${COMPOSE_FILE}")
ENV_STATE_DIR="/home/gabrielnatalnet/.rap-deploy"
ENV_STATE_FILE="${ENV_STATE_DIR}/web-env.sha256"
REBUILD=false

fail() {
    echo "[ERRO] $*" >&2
    exit 1
}

if [[ "${1:-}" == "--rebuild" ]]; then
    REBUILD=true
elif [[ $# -gt 0 ]]; then
    fail "Uso: $0 [--rebuild]"
fi

[[ -d "${PROJECT_DIR}" ]] || fail "Diretorio canonico inexistente: ${PROJECT_DIR}"
[[ -f "${COMPOSE_FILE}" ]] || fail "Compose inexistente: ${COMPOSE_FILE}"
cd "${PROJECT_DIR}"

echo "[OK] Projeto canonico: ${PROJECT_DIR}"
command -v docker-compose >/dev/null || fail "docker-compose legado nao encontrado"
docker --version
compose_version=$(docker-compose version --short 2>/dev/null || docker-compose --version)
echo "[INFO] docker-compose: ${compose_version}"
if [[ "${compose_version}" == 1.29.2* ]]; then
    echo "[AVISO] Docker Compose v1.29.2 esta obsoleto e pode falhar com ContainerConfig no Docker Engine atual."
    echo "[AVISO] O deploy nao usara --force-recreate. Solicite Compose v2 ao administrador quando possivel."
fi
"${COMPOSE[@]}" config -q || fail "docker-compose.yml invalido"

db_id=$("${COMPOSE[@]}" ps -q db)
[[ -n "${db_id}" ]] || fail "Servico db do projeto public nao encontrado"

db_running=$(docker inspect --format '{{.State.Running}}' "${db_id}")
db_health=$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}sem-healthcheck{{end}}' "${db_id}")
db_project=$(docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "${db_id}")
db_service=$(docker inspect --format '{{index .Config.Labels "com.docker.compose.service"}}' "${db_id}")
db_volume=$(docker inspect --format '{{range .Mounts}}{{if eq .Destination "/var/lib/postgresql/data"}}{{.Type}}:{{.Name}}{{end}}{{end}}' "${db_id}")

[[ "${db_running}" == "true" ]] || fail "PostgreSQL nao esta Up"
[[ "${db_health}" == "healthy" ]] || fail "PostgreSQL nao esta healthy: ${db_health}"
[[ "${db_project}" == "public" && "${db_service}" == "db" ]] || fail "Container DB pertence a outro projeto/servico"
[[ "${db_volume}" == "volume:${EXPECTED_DB_VOLUME}" ]] || fail "Volume inesperado em /var/lib/postgresql/data: ${db_volume:-nenhum}"

echo "[OK] PostgreSQL saudavel"
echo "[OK] Volume de producao: ${EXPECTED_DB_VOLUME}"
echo "[OK] Banco nao sera recriado durante este deploy"

[[ -f "${PROJECT_DIR}/.env" ]] || fail ".env de producao nao encontrado"
current_env_hash=$(sha256sum "${PROJECT_DIR}/.env" | awk '{print $1}')
if [[ -f "${ENV_STATE_FILE}" ]]; then
    deployed_env_hash=$(<"${ENV_STATE_FILE}")
    if [[ "${current_env_hash}" != "${deployed_env_hash}" && "${REBUILD}" != "true" ]]; then
        echo "[AVISO] Alteracao de ambiente detectada."
        fail "E necessario recriar somente o web: ./scripts/recreate-web-production.sh"
    fi
else
    echo "[AVISO] Ainda nao existe referencia segura do .env carregado pelo web."
    echo "[AVISO] Se o .env mudou, use recreate-web-production.sh; o conteudo nao foi exibido."
fi

if [[ "${REBUILD}" == "true" ]]; then
    echo "[INFO] Construindo somente a imagem web; o web atual continua ativo"
    "${COMPOSE[@]}" build web
fi

run_isolated() {
    "${COMPOSE[@]}" run --rm --no-deps -T \
        -e DJANGO_SETTINGS_MODULE=rap.settings_test \
        -e EMAIL_BACKEND=django.core.mail.backends.locmem.EmailBackend \
        -e DATABASE_URL=sqlite:///:memory: \
        -e DJANGO_SECRET_KEY=test-only-not-used-in-production-000000000000000000 \
        web "$@"
}

echo "[INFO] Validando Django sem acessar o banco de producao"
"${COMPOSE[@]}" run --rm --no-deps -T web python manage.py check
"${COMPOSE[@]}" run --rm --no-deps -T web python manage.py makemigrations --check --dry-run
run_isolated python manage.py check --settings=rap.settings_test
run_isolated python manage.py makemigrations --check --dry-run --settings=rap.settings_test

echo "[INFO] Executando testes criticos de autenticacao"
run_isolated python manage.py test Usuario.tests_auth --settings=rap.settings_test --noinput

echo "[INFO] Consultando o plano de migrations no banco de producao (somente leitura)"
if ! migration_plan=$("${COMPOSE[@]}" run --rm --no-deps -T web python manage.py migrate --plan); then
    fail "Nao foi possivel calcular o plano de migrations"
fi
printf '%s\n' "${migration_plan}"

if ! migration_state=$("${COMPOSE[@]}" run --rm --no-deps -T web python manage.py shell -c \
    "from django.db import connection; from django.db.migrations.executor import MigrationExecutor; executor=MigrationExecutor(connection); print('PENDING' if executor.migration_plan(executor.loader.graph.leaf_nodes()) else 'NO_PENDING')"); then
    fail "Nao foi possivel confirmar migrations pendentes"
fi

if [[ "${migration_state}" == *"PENDING" && "${migration_state}" != *"NO_PENDING"* ]]; then
    umask 077
    mkdir -p "${BACKUP_DIR}"
    timestamp=$(date '+%Y%m%d_%H%M%S')
    backup_file="${BACKUP_DIR}/rap_antes_migracoes_${timestamp}.sql"
    partial_file="${backup_file}.incompleto"

    echo "[INFO] Existem migrations pendentes; criando backup antes de aplica-las"
    if ! "${COMPOSE[@]}" exec -T db sh -c \
        'exec pg_dump --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" --no-owner --no-privileges' \
        >"${partial_file}"; then
        fail "pg_dump falhou; migrations NAO foram aplicadas. Arquivo parcial: ${partial_file}"
    fi
    [[ -s "${partial_file}" ]] || fail "Backup vazio; migrations NAO foram aplicadas"
    mv "${partial_file}" "${backup_file}"
    echo "[OK] Backup verificado: ${backup_file}"

    "${COMPOSE[@]}" run --rm --no-deps -T web python manage.py migrate --noinput
else
    echo "[OK] Nenhuma migration pendente; backup pre-migration nao e necessario"
fi

echo "[INFO] Coletando arquivos estaticos"
"${COMPOSE[@]}" run --rm --no-deps -T web python manage.py collectstatic --noinput

if [[ "${REBUILD}" == "true" ]]; then
    echo "[INFO] Recriando somente o servico web pelo fluxo compativel com Compose v1"
    "${PROJECT_DIR}/scripts/recreate-web-production.sh"
else
    echo "[INFO] Reiniciando somente o servico web"
    "${COMPOSE[@]}" restart web
fi

web_id=$("${COMPOSE[@]}" ps -q web)
[[ -n "${web_id}" ]] || fail "Servico web nao foi encontrado apos o restart"

echo "[INFO] Aguardando o healthcheck do web (ate 120 segundos)"
for _ in $(seq 1 24); do
    web_running=$(docker inspect --format '{{.State.Running}}' "${web_id}")
    web_health=$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}sem-healthcheck{{end}}' "${web_id}")
    if [[ "${web_running}" == "true" && "${web_health}" == "healthy" ]]; then
        break
    fi
    sleep 5
done

web_running=$(docker inspect --format '{{.State.Running}}' "${web_id}")
web_health=$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}sem-healthcheck{{end}}' "${web_id}")
if [[ "${web_running}" != "true" || "${web_health}" != "healthy" ]]; then
    "${COMPOSE[@]}" logs --tail=30 web >&2 || true
    fail "Web nao ficou saudavel: running=${web_running} health=${web_health}"
fi

docker exec "${web_id}" python -c \
    "import urllib.request; r=urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8000/health/', headers={'Host':'rap.natalnet.br','X-Forwarded-Proto':'https'}), timeout=5); assert r.status == 200"

echo "[OK] Porta 8000 e /health/ responderam dentro do container"
echo "[SUCESSO] Deploy concluido; somente o web foi reiniciado"
