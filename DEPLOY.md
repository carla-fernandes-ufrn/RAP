# Deploy seguro do RAP

Este procedimento foi preparado para o servidor Ubuntu da UFRN, Docker 29.1.3 e
`docker-compose` legado 1.29.2. Ele nunca usa `docker compose`.

## Arquitetura

```text
Internet -> Nginx :80/:443 -> Gunicorn/Django :8000 -> PostgreSQL 16
```

O projeto Compose chama-se sempre `public`. O diretório canônico é
`/home/web/Sites/rap/public`; `/var/www/sftp-jails/rap/data` é apenas a visão SFTP
da mesma pasta física.

Todos os comandos Compose deste documento significam:

```bash
docker-compose -p public -f /home/web/Sites/rap/public/docker-compose.yml
```

Nunca execute Compose a partir do caminho SFTP sem `-p` e `-f` explícitos.

## Proteção do banco

O banco real foi identificado por inspeção do `public_db_1`:

```text
status=running health=healthy
project=public service=db
type=volume name=public_pgdata destination=/var/lib/postgresql/data
```

O Compose declara `public_pgdata` como volume externo explicitamente nomeado.
Assim, o PostgreSQL possui persistência independente do container e do ciclo de
vida da aplicação. O deploy confere container, labels, saúde, tipo, destino e nome
do volume e aborta se qualquer item divergir. Ele nunca recria o serviço `db`.

Antes da primeira mudança, valide novamente, sem alterar nada:

```bash
docker inspect public_db_1 --format 'status={{.State.Status}} health={{if .State.Health}}{{.State.Health.Status}}{{else}}sem-healthcheck{{end}}'
docker inspect public_db_1 --format '{{range .Mounts}}{{if eq .Destination "/var/lib/postgresql/data"}}type={{.Type}} name={{.Name}} destination={{.Destination}}{{end}}{{end}}'
docker volume inspect public_pgdata
docker-compose -p public -f /home/web/Sites/rap/public/docker-compose.yml config
```

O último comando deve reconhecer o volume externo existente. Não prossiga se o
nome não for exatamente `public_pgdata` ou se o banco não estiver `healthy`.

## Nunca executar

```bash
docker-compose down
docker-compose down -v
docker rm -f public_web_1
docker volume rm public_pgdata
docker system prune --volumes
```

Também não execute `docker-compose up -d` sem indicar o serviço. Nenhum script
deste projeto contém esses comandos destrutivos.

## Primeira transição segura

Envie os arquivos alterados pelo FileZilla e então entre pelo SSH:

```bash
cd /home/web/Sites/rap/public
chmod +x scripts/*.sh entrypoint.sh
./scripts/status-production.sh
docker inspect public_db_1 --format 'restart={{.HostConfig.RestartPolicy.Name}}'
```

Se a política atual do DB não for `unless-stopped`, a alteração pontual abaixo
não reinicia nem recria o banco; apenas configura seu retorno após reboot:

```bash
docker update --restart unless-stopped public_db_1
```

Valide a configuração antes de tocar no web:

```bash
docker-compose -p public -f /home/web/Sites/rap/public/docker-compose.yml config -q
```

Como a primeira entrega muda `Dockerfile`, `requirements.txt` e o healthcheck,
faça uma construção controlada. O DB permanece rodando durante todo o processo:

```bash
./scripts/deploy-production.sh --rebuild
./scripts/status-production.sh
```

O `.env` existente precisa conter `DJANGO_SECRET_KEY` (ou o nome legado
`SECRET_KEY`) com pelo menos 50 caracteres. Não envie nem substitua esse arquivo
pelo FileZilla. Se a validação acusar chave ausente/fraca, pare e ajuste apenas
essa variável no arquivo já existente, sem mostrar seu valor no terminal ou no
histórico do shell.

Não faça a primeira transição se o Compose informar volume externo ausente. Isso
indica divergência de ambiente e deve ser investigado, nunca corrigido criando um
volume vazio.

## Atualização via FileZilla

1. Envie somente os arquivos alterados.
2. Nunca sobrescreva `.env`.
3. Nunca envie `media/`.
4. Nunca envie `staticfiles/`.
5. Nunca envie `dump.json`, dumps ou backups SQL.
6. Execute o deploy seguro pelo SSH.
7. Confirme `/health/` e o status.
8. Teste login/cadastro quando o código correspondente mudar.

Como `.:/app` é um bind mount, Python, templates, CSS e JavaScript não exigem
rebuild. O upload muda os arquivos visíveis no container, mas os workers só são
reiniciados depois das validações.

## Deploy normal

```bash
cd /home/web/Sites/rap/public
./scripts/deploy-production.sh
./scripts/status-production.sh
```

O fluxo valida DB/volume, Django, migrations e testes críticos; cria backup se
necessário; aplica migrations; coleta estáticos; reinicia somente `web`; aguarda o
healthcheck e testa `/health/` na porta 8000.

## Deploy com requirements novos

Use apenas quando `Dockerfile`, `requirements.txt`, `.dockerignore` ou dependências
da imagem mudarem:

```bash
cd /home/web/Sites/rap/public
./scripts/deploy-production.sh --rebuild
```

Internamente são usados `build web` e `up -d --no-deps --force-recreate web`.
O serviço `db` não é iniciado, parado ou recriado.

## Migrations

O script executa primeiro `migrate --plan`. Quando há operações pendentes, ele só
executa `migrate --noinput` depois de um `pg_dump` bem-sucedido e não vazio. Se
qualquer validação, teste ou backup falhar, o deploy aborta antes do restart e o
web atual continua rodando.

`entrypoint.sh` não executa migrations automaticamente. Isso impede que uma mera
recriação do web altere o banco sem o backup e as guardas do deploy.

## Backups

Os backups ficam fora da pasta publicada pelo FileZilla:

```text
/home/gabrielnatalnet/rap-backups/rap_antes_migracoes_YYYYMMDD_HHMMSS.sql
```

O diretório é criado com permissões restritas (`umask 077`). O script não remove
backups. Um arquivo `.incompleto` significa que `pg_dump` falhou e nenhuma migration
foi aplicada. Não imprima nem compartilhe o conteúdo: ele contém dados reais.

Para um backup manual, use o mesmo padrão e confirme que o arquivo não está vazio;
prefira o backup automático imediatamente antes das migrations para evitar erros
de credenciais e caminhos.

## Testes

Os testes críticos do deploy usam `rap.settings_test`, SQLite em memória e o
backend de e-mail em memória. Portanto não acessam `appdb`, PostgreSQL, internet ou
SMTP, mesmo que o `.env` de produção esteja carregado:

```bash
docker-compose -p public -f /home/web/Sites/rap/public/docker-compose.yml run --rm --no-deps -T \
  -e DJANGO_SETTINGS_MODULE=rap.settings_test \
  -e EMAIL_BACKEND=django.core.mail.backends.locmem.EmailBackend \
  -e DATABASE_URL=sqlite:///:memory: \
  web python manage.py test Usuario.tests_auth --settings=rap.settings_test
```

Para construir a imagem e executar a suíte completa em ambiente isolado:

```bash
./scripts/test-production-build.sh
```

Os testes verificam login válido/inválido, área protegida, os quatro tipos de
usuário, cadastro e validações, geração de código, e-mail sem senha, confirmação,
expiração/reuso e o fluxo completo de recuperação e troca de senha. `mail.outbox`
captura as mensagens; nenhuma mensagem real é enviada.

## Teste manual do SMTP de produção

Este teste é separado e nunca roda no deploy. Ele exige um destinatário explícito:

```bash
./scripts/test-email-production.sh endereco-controlado@example.com
```

Ele envia uma única mensagem real e não imprime a senha SMTP.

## Healthcheck

`GET /health/` não exige login, faz apenas `SELECT 1` e responde
`{"status":"ok"}` com HTTP 200. Não expõe credenciais, versões ou detalhes do
banco. O healthcheck Docker usa Python/`urllib`, sem depender de `curl`.

## Rollback

Para alteração somente de código, restaure os arquivos da versão anterior, rode
as mesmas validações e execute `./scripts/deploy-production.sh`. Reinicie somente
o web.

Não reverta migrations nem restaure o PostgreSQL automaticamente. Rollback de
schema ou dados pode destruir informação criada após o deploy e deve ser avaliado
com o administrador da UFRN. Preserve o dump pré-migration para emergência.

## Porta PostgreSQL e riscos administrativos

O Compose ainda publica `5432:5432` para preservar compatibilidade com possíveis
integrações da UFRN. Isso aumenta a superfície de ataque. Se o administrador
confirmar que somente o Django usa o DB pela rede Docker, remova a publicação e
mantenha o PostgreSQL apenas na rede interna.

Também dependem do administrador: regras do firewall/Nginx, TLS e cabeçalhos de
proxy, política de retenção e cópia externa dos backups, rotação da credencial
legada do PostgreSQL/SMTP e monitoramento de disco. A rotação de credenciais não
deve ser misturada ao primeiro deploy seguro.
