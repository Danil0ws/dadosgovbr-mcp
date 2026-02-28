FROM python:3.12-slim

# Metadados da imagem
LABEL maintainer="dadosgovbr-mcp"
LABEL description="Servidor MCP para dados abertos do Brasil"
LABEL version="1.0"

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv para gerenciamento de pacotes Python
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências primeiro (para cache de build)
COPY pyproject.toml ./
COPY uv.lock* ./

# Instalar dependências Python
RUN uv sync --frozen --no-dev --no-cache

# Copiar código-fonte
COPY main.py ./
COPY helpers/ ./helpers/
COPY tools/ ./tools/

# Criar usuário não-root para segurança
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${MCP_PORT}/health || exit 1

# Expor porta
EXPOSE ${MCP_PORT}

# Iniciar o servidor
CMD ["uv", "run", "python", "main.py"]
