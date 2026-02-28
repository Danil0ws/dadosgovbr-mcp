# dadosgovbr-mcp

[![Licença: MIT](https://img.shields.io/badge/Licença-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

Servidor [Model Context Protocol (MCP)](https://modelcontextprotocol.io) para dados abertos do Brasil. Permite que chatbots de IA (Claude, ChatGPT, Gemini, etc.) pesquisem, explorem e analisem conjuntos de dados dos portais governamentais brasileiros diretamente por conversa.

Ao invés de acessar manualmente os sites, você pode perguntar diretamente ao seu assistente coisas como:
- *"Quais conjuntos de dados existem sobre transporte público em São Paulo?"*
- *"Mostre-me os dados de multas pagas disponíveis no Portal SP"*
- *"Liste as organizações com dados sobre saúde no portal federal"*
- *"Analise o conteúdo do arquivo CSV de infrações de trânsito"*

## Portais Suportados

| Portal | URL | API |
|--------|-----|-----|
| Dados Abertos SP | [dadosabertos.sp.gov.br](https://dadosabertos.sp.gov.br) | CKAN 2.x (pública) |
| Portal Federal | [dados.gov.br](https://dados.gov.br) | CKAN 2.x |

## 🚀 Próximas Features (Em Breve)

Expansão para portais de órgãos federais específicos com dados **mais atualizados** e **documentação técnica detalhada** direto da fonte:

| Portal | URL | Tipo de Dados | Status |
|--------|-----|---------------|--------|
| **Banco Central (BCB)** | [dadosabertos.bcb.gov.br](https://dadosabertos.bcb.gov.br) | Taxas de juros, câmbio, indicadores econômicos | 📋 Planejado |
| **Portal da Transparência** | [portaldatransparencia.gov.br](https://portaldatransparencia.gov.br/download-de-dados) | Gastos públicos, convênios, servidores | 📋 Planejado |
| **CVM** | [dados.cvm.gov.br](https://dados.cvm.gov.br) | Empresas em bolsa, fundos de investimento, regulamentação | 📋 Planejado |
| **DataSUS** | [opendatasus.saude.gov.br](https://opendatasus.saude.gov.br) | Saúde, vacinação, registros hospitalares | 📋 Planejado |
| **Câmara dos Deputados** | [dadosabertos.camara.leg.br](https://dadosabertos.camara.leg.br) | Legislativo, votações, deputados | 📋 Planejado |

Interessado em contribuir? Abra uma [discussão](https://github.com/seu-usuario/dadosgovbr-mcp/discussions) ou um [PR](https://github.com/seu-usuario/dadosgovbr-mcp/pulls)!

## Ferramentas Disponíveis

### Portal SP (`dadosabertos.sp.gov.br`)

| Ferramenta | Descrição |
|-----------|-----------|
| `sp_buscar_conjuntos` | Pesquisa conjuntos de dados por palavras-chave |
| `sp_detalhes_conjunto` | Metadados completos de um conjunto específico |
| `sp_listar_recursos` | Lista todos os arquivos de um conjunto |
| `sp_detalhes_recurso` | Metadados de um arquivo específico |
| `sp_baixar_e_analisar_recurso` | Download e análise de conteúdo (CSV, JSON, XLSX...) |
| `sp_listar_organizacoes` | Lista órgãos e entidades do Governo SP |
| `sp_listar_grupos` | Lista temas/categorias disponíveis |

### Portal Federal (`dados.gov.br`)

| Ferramenta | Descrição |
|-----------|-----------|
| `federal_buscar_conjuntos` | Pesquisa conjuntos de dados por palavras-chave |
| `federal_detalhes_conjunto` | Metadados completos de um conjunto específico |
| `federal_listar_recursos` | Lista todos os arquivos de um conjunto |
| `federal_detalhes_recurso` | Metadados de um arquivo específico |
| `federal_baixar_e_analisar_recurso` | Download e análise de conteúdo (CSV, JSON, XLSX...) |
| `federal_listar_organizacoes` | Lista ministérios e autarquias federais |
| `federal_listar_temas` | Lista temas/categorias disponíveis |

## Conectando seu Chatbot

Use o endpoint hospedado (quando disponível) ou execute localmente.

---

### Claude Desktop

Edite o arquivo de configuração do Claude Desktop:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "dadosgovbr": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://dadosgovbr-mcp.onrender.com/mcp"
      ]
    }
  }
}
```

---

### Claude Code

```bash
claude mcp add --transport http dadosgovbr https://dadosgovbr-mcp.onrender.com/mcp
```

---

### VS Code

Adicione ao `settings.json`:

```json
{
  "servers": {
    "dadosgovbr": {
      "url": "https://dadosgovbr-mcp.onrender.com/mcp",
      "type": "http"
    }
  }
}
```

---

### Cursor

Abra as configurações do Cursor, procure por "MCP" e adicione:

```json
{
  "mcpServers": {
    "dadosgovbr": {
      "url": "https://dadosgovbr-mcp.onrender.com/mcp",
      "transport": "http"
    }
  }
}
```

---

### Windsurf

Edite `~/.codeium/mcp_config.json`:

```json
{
  "mcpServers": {
    "dadosgovbr": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://dadosgovbr-mcp.onrender.com/mcp"]
    }
  }
}
```

---

### Gemini CLI

Edite `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "dadosgovbr": {
      "httpUrl": "https://dadosgovbr-mcp.onrender.com/mcp"
    }
  }
}
```

---

### AnythingLLM

Localize o arquivo `anythingllm_mcp_servers.json` em:
- **macOS**: `~/Library/Application Support/anythingllm-desktop/storage/plugins/anythingllm_mcp_servers.json`
- **Linux**: `~/.config/anythingllm-desktop/storage/plugins/anythingllm_mcp_servers.json`
- **Windows**: `C:\Users\<usuario>\AppData\Roaming\anythingllm-desktop\storage\plugins\anythingllm_mcp_servers.json`

```json
{
  "mcpServers": {
    "dadosgovbr": {
      "type": "streamable",
      "url": "https://dadosgovbr-mcp.onrender.com/mcp"
    }
  }
}
```

---

## Executando Localmente

### Pré-requisitos

- Python 3.11 ou superior
- [uv](https://github.com/astral-sh/uv) (gerenciador de pacotes Python recomendado) **ou** Docker

---

### Com Docker (Recomendado)

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/dadosgovbr-mcp.git
cd dadosgovbr-mcp

# Iniciar com as configurações padrão (porta 8000)
docker compose up -d

# Iniciar com configurações personalizadas
MCP_PORT=8007 docker compose up -d

# Verificar status
docker compose ps

# Parar o servidor
docker compose down
```

**Variáveis de ambiente disponíveis:**

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `MCP_HOST` | `0.0.0.0` | Host do servidor. Use `127.0.0.1` para dev local |
| `MCP_PORT` | `8000` | Porta do servidor HTTP MCP |

---

### Instalação Manual (uv)

O [uv](https://github.com/astral-sh/uv) é o gerenciador de pacotes recomendado por ser mais rápido e confiável que pip.

**1. Instalar o uv** (se ainda não tiver):

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex
```

**2. Clonar o repositório e instalar dependências:**

```bash
git clone https://github.com/seu-usuario/dadosgovbr-mcp.git
cd dadosgovbr-mcp
uv sync
```

**3. Configurar variáveis de ambiente:**

```bash
cp .env.example .env
# Edite o .env conforme necessário
```

**4. Iniciar o servidor:**

```bash
uv run python main.py
```

O servidor estará disponível em `https://dadosgovbr-mcp.onrender.com/mcp`.


## Transporte Suportado

Este servidor MCP utiliza o **Streamable HTTP transport** exclusivamente.

**STDIO e SSE não são suportados.**

### Endpoints Disponíveis

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/mcp` | `POST` | Mensagens JSON-RPC (cliente → servidor) |
| `/health` | `GET` | Verificação de saúde (`{"status":"ok"}`) |

---

## Testes

### Testes Unitários (sem rede)

```bash
# Executar todos os testes unitários
uv run pytest tests/test_helpers.py -v

# Com cobertura de código
uv run pytest tests/test_helpers.py -v --cov=helpers
```

### Testes de Integração (requerem rede)

```bash
# Testes do Portal SP
uv run pytest tests/test_sp.py -m integration -v

# Testes do Portal Federal
uv run pytest tests/test_federal.py -m integration -v

# Todos os testes de integração
uv run pytest -m integration -v
```

### Todos os Testes

```bash
uv run pytest -v
```

### Inspeção Interativa com MCP Inspector

Use o [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) para testar o servidor interativamente:

```bash
# Iniciar o servidor primeiro
uv run python main.py

# Em outro terminal, iniciar o inspector
npx @modelcontextprotocol/inspector --http-url "https://dadosgovbr-mcp.onrender.com/mcp"
```

---

## Desenvolvimento

### Linting e Formatação

Este projeto usa [Ruff](https://astral.sh/ruff/) para linting e formatação de código.

```bash
# Verificar e corrigir problemas de linting
uv run ruff check --fix

# Formatar o código
uv run ruff format

# Verificar tipos (ty)
uv run ty check
```

### Hooks de Pre-commit

```bash
# Instalar os hooks
uv run pre-commit install

# Executar manualmente em todos os arquivos
uv run pre-commit run --all-files
```

Os hooks executam automaticamente a cada `git commit`:
- Verificação de sintaxe YAML e TOML
- Correção de fim de arquivo
- Remoção de espaços em branco extras
- Verificação de arquivos grandes
- Linting e formatação com Ruff

---

## Estrutura do Projeto

```
dadosgovbr-mcp/
├── main.py                  # Ponto de entrada do servidor MCP
├── pyproject.toml           # Configuração do projeto e dependências
├── Dockerfile               # Imagem Docker
├── docker-compose.yml       # Orquestração Docker
├── .env.example             # Exemplo de variáveis de ambiente
├── .gitignore
├── .pre-commit-config.yaml  # Hooks de pre-commit
├── helpers/
│   ├── __init__.py
│   ├── http.py              # Cliente HTTP assíncrono (httpx)
│   ├── parser.py            # Parsing de CSV, JSON, XLSX, etc.
│   └── formatter.py         # Formatação de respostas para MCP
├── tools/
│   ├── __init__.py
│   ├── sp.py                # Ferramentas para dadosabertos.sp.gov.br
│   └── federal.py           # Ferramentas para dados.gov.br
└── tests/
    ├── __init__.py
    ├── test_helpers.py      # Testes unitários dos helpers
    ├── test_sp.py           # Testes de integração - Portal SP
    └── test_federal.py      # Testes de integração - Portal Federal
```

---

## Formatos de Arquivo Suportados

Para análise e download de recursos:

| Formato | Suporte |
|---------|---------|
| CSV | Completo (UTF-8, Latin-1, CP1252; delimitadores `,` `;` `\t` `\|`) |
| CSV.GZ | Completo (descompressão automática) |
| JSON | Completo (arrays e objetos com listas) |
| JSONL / NDJSON | Completo |
| XLSX | Completo (requer `openpyxl`) |
| XLS | Completo (via `openpyxl`) |

---

## Contribuindo

Contribuições são bem-vindas! Antes de enviar um PR, por favor siga estas diretrizes:

- **Mantenha pequeno:** Seguimos o fluxo **1 funcionalidade = 1 PR**.
- **Revise o código:** Não envie código gerado por IA sem revisão humana. Todo código deve ser revisado e testado antes do envio.
- **Execute os testes:** Certifique-se de que todos os testes passam.
- **Siga o estilo:** Execute `ruff check --fix && ruff format` antes de commitar.

### Processo de Contribuição

1. Faça um fork do repositório
2. Crie uma branch a partir de `main`: `git checkout -b minha-funcionalidade`
3. Implemente as mudanças com testes
4. Execute `uv run ruff check --fix && uv run ruff format`
5. Faça commit e abra um Pull Request

---

## Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).

---

## Recursos Relacionados

- [Portal de Dados Abertos SP](https://dadosabertos.sp.gov.br)
- [Portal Federal de Dados Abertos](https://dados.gov.br)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [datagouv-mcp](https://github.com/datagouv/datagouv-mcp) — Inspiração deste projeto (Portal Francês)
