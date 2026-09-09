FROM python:3.12-slim

# Evita buffer do Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Sistema básico + cliente psql para diagnósticos
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev postgresql-client \
 && rm -rf /var/lib/apt/lists/*

RUN adduser --disabled-password --gecos "" appuser

# Diretório da app
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar projeto
COPY --chown=appuser:appuser . /app
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Executa a aplicação sem privilégios de root.
RUN mkdir -p /app/staticfiles /app/media \
 && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
