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
Os volumes reais `public_media` e `public_staticfiles` também são referenciados
explicitamente como externos; nenhum volume novo é criado por mudança no nome do
diretório ou projeto.

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

Também não execute `docker-compose up -d` sem indicar o serviço. A única exceção
controlada é `recreate-web-production.sh`: ele remove pelo ID apenas o container
confirmado como serviço `web`, sem `-v`, depois de validar DB e `public_pgdata`.
Ele jamais aceita ou remove o serviço `db`.

## Diagnóstico 502

O 502 ocorreu porque Nginx continuou atendendo enquanto nenhum Gunicorn escutava
na porta 8000. O web tinha sido removido durante um ciclo de `down`, remoção e
`up`; o PostgreSQL permaneceu saudável. Os scripts atuais não derrubam a stack e
sempre aguardam `/health/` depois de alterar exclusivamente o web.

## Compatibilidade do Compose e ContainerConfig

O servidor combina Docker Engine 29.1.3 com `docker-compose` Python 1.29.2,
obsoleto. Esse Compose v1 tenta consultar o campo antigo `ContainerConfig` nos
metadados de imagem do Docker atual e pode terminar com `KeyError:
'ContainerConfig'`.

Por isso nenhum fluxo usa `--force-recreate`. Quando uma recriação é realmente
necessária, o script valida o banco, para e remove somente o container web sem
volumes e executa:

```bash
docker-compose -p public -f /home/web/Sites/rap/public/docker-compose.yml \
  up -d --no-deps --no-build web
```

Os scripts mostram as versões e um aviso ao detectar 1.29.2. Não instalam nada.
A correção estrutural futura é o administrador da UFRN instalar Compose v2.

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

Internamente são usados `build web` e, depois das validações, o fluxo compatível
de `recreate-web-production.sh`, sem `--force-recreate`. O serviço `db` não é
iniciado, parado ou recriado.

## Alteração de `.env`

Variáveis de `env_file` são copiadas para o container quando ele é criado.
`docker restart`, `docker start` e `docker-compose restart` reutilizam o mesmo
container e mantêm os valores antigos.

Depois de uma alteração manual e controlada do `.env`, execute:

```bash
cd /home/web/Sites/rap/public
./scripts/recreate-web-production.sh
./scripts/status-production.sh
```

O script calcula somente o SHA-256 do arquivo e guarda a referência em
`/home/gabrielnatalnet/.rap-deploy/web-env.sha256`. O conteúdo nunca é exibido.
Se um deploy normal detectar hash diferente, ele aborta e pede a recriação do
web. O `.env` nunca deve ser enviado pelo FileZilla.

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

Ele envia uma única mensagem real, usa `fail_silently=False`, não acessa o banco,
não executa migrations, não reinicia containers e não imprime a senha SMTP. Exit
code diferente de zero indica falha.

## SMTP

O incidente confirmado não era a configuração atual do `.env`: um container web
antigo ainda continha credenciais SMTP anteriores e recebeu erro Gmail 535. Um
container temporário carregou o arquivo atual e entregou normalmente. A recriação
exclusiva do web resolveu o problema.

O código não usa mais `fail_silently=True`. Falhas são registradas com tipo e ID
interno do usuário, sem OTP, e-mail, senha ou conteúdo. No cadastro, a conta
inativa é preservada e a tela oferece “Reenviar código”. Um código cujo envio
falhou é descartado; quando o reenvio funciona, códigos anteriores são marcados
como utilizados. A recuperação mantém resposta genérica para não enumerar contas.

Aceitação SMTP não garante caixa de entrada: filtros, spam e políticas do domínio
ainda podem interferir. Use o teste manual e um endereço controlado.

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

## Comandos por tipo de atualização

### A) Somente código, templates, CSS ou JavaScript

```bash
cd /home/web/Sites/rap/public
./scripts/deploy-production.sh
```

### B) Requirements, Dockerfile ou `.dockerignore`

```bash
cd /home/web/Sites/rap/public
./scripts/deploy-production.sh --rebuild
```

### C) `.env` alterado manualmente

```bash
cd /home/web/Sites/rap/public
./scripts/recreate-web-production.sh
./scripts/status-production.sh
```

Se código e imagem também mudaram, `deploy-production.sh --rebuild` já termina
pela mesma recriação segura e registra o novo hash.

### D) Migrations pendentes

Não rode `migrate` manualmente. Execute o deploy correspondente a A ou B. O script
mostra `migrate --plan`, gera e valida o dump e só então aplica a migration.

## Porta PostgreSQL e riscos administrativos

O Compose ainda publica `5432:5432` para preservar compatibilidade com possíveis
integrações da UFRN. Isso aumenta a superfície de ataque. Se o administrador
confirmar que somente o Django usa o DB pela rede Docker, remova a publicação e
mantenha o PostgreSQL apenas na rede interna.

Também dependem do administrador: regras do firewall/Nginx, TLS e cabeçalhos de
proxy, política de retenção e cópia externa dos backups, rotação da credencial
legada do PostgreSQL/SMTP e monitoramento de disco. A rotação de credenciais não
deve ser misturada ao primeiro deploy seguro.
