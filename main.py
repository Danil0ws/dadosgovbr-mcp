"""
Servidor MCP para dados abertos do Brasil.

Permite que chatbots de IA pesquisem, explorem e analisem conjuntos de dados
dos portais de dados abertos brasileiros diretamente por conversa.

Portais suportados:
- dadosabertos.sp.gov.br (Governo do Estado de São Paulo)
- dados.gov.br (Portal Federal de Dados Abertos)
"""

import os
import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

from tools.sp import (
    buscar_conjuntos_sp,
    detalhes_conjunto_sp,
    listar_recursos_sp,
    detalhes_recurso_sp,
    baixar_e_analisar_recurso_sp,
    listar_organizacoes_sp,
    listar_grupos_sp,
)
from tools.federal import (
    buscar_conjuntos_federal,
    detalhes_conjunto_federal,
    listar_recursos_federal,
    detalhes_recurso_federal,
    baixar_e_analisar_recurso_federal,
    listar_organizacoes_federal,
    listar_temas_federal,
)

# ──────────────────────────────────────────────────────────────────────────────
# Inicialização da aplicação FastAPI
# ──────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação."""
    yield

app = FastAPI(title="dadosgovbr-mcp", lifespan=lifespan)

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "dadosgovbr-mcp"}

# Instância do FastMCP
mcp = FastMCP(
    name="dadosgovbr-mcp",
    instructions=(
        "Servidor MCP para dados abertos do Brasil. "
        "Permite pesquisar, explorar e analisar conjuntos de dados dos portais "
        "dadosabertos.sp.gov.br (São Paulo) e dados.gov.br (Federal). "
        "Use as ferramentas disponíveis para encontrar e analisar dados governamentais brasileiros."
    ),
)

# ──────────────────────────────────────────────────────────────────────────────
# Ferramentas: Portal de Dados Abertos SP (dadosabertos.sp.gov.br)
# ──────────────────────────────────────────────────────────────────────────────


@mcp.tool()
async def sp_buscar_conjuntos(
    consulta: str,
    pagina: int = 1,
    tamanho_pagina: int = 20,
) -> str:
    """
    Pesquisa conjuntos de dados no Portal de Dados Abertos do Estado de São Paulo (dadosabertos.sp.gov.br).

    Retorna conjuntos de dados com metadados (título, descrição, organização, tags, quantidade de recursos).

    Args:
        consulta: Termos de pesquisa (ex.: "saude", "educacao", "transporte")
        pagina: Número da página (padrão: 1)
        tamanho_pagina: Quantidade de resultados por página (padrão: 20, máximo: 100)
    """
    return await buscar_conjuntos_sp(consulta, pagina, tamanho_pagina)


@mcp.tool()
async def sp_detalhes_conjunto(
    id_conjunto: str,
) -> str:
    """
    Obtém informações detalhadas sobre um conjunto de dados específico do Portal SP.

    Retorna metadados completos: título, descrição, organização, tags, datas, licença, etc.

    Args:
        id_conjunto: ID ou slug do conjunto de dados (ex.: "multas-pagas" ou UUID)
    """
    return await detalhes_conjunto_sp(id_conjunto)


@mcp.tool()
async def sp_listar_recursos(
    id_conjunto: str,
) -> str:
    """
    Lista todos os recursos (arquivos) disponíveis em um conjunto de dados do Portal SP.

    Retorna metadados de cada recurso: formato, tamanho, tipo, URL de download.

    Args:
        id_conjunto: ID ou slug do conjunto de dados
    """
    return await listar_recursos_sp(id_conjunto)


@mcp.tool()
async def sp_detalhes_recurso(
    id_recurso: str,
) -> str:
    """
    Obtém informações detalhadas sobre um recurso (arquivo) específico do Portal SP.

    Retorna formato, tamanho, tipo MIME, URL de download e conjunto de dados associado.

    Args:
        id_recurso: ID UUID do recurso
    """
    return await detalhes_recurso_sp(id_recurso)


@mcp.tool()
async def sp_baixar_e_analisar_recurso(
    id_recurso: str,
    max_linhas: int = 20,
    max_tamanho_mb: int = 500,
) -> str:
    """
    Faz o download e analisa o conteúdo de um recurso do Portal SP.

    Suporta os formatos: CSV, CSV.GZ, JSON, JSONL, XLSX, XLS.
    Útil para visualizar amostras dos dados sem baixar o arquivo completo.

    Args:
        id_recurso: ID UUID do recurso
        max_linhas: Número máximo de linhas a retornar (padrão: 20)
        max_tamanho_mb: Tamanho máximo do arquivo em MB (padrão: 500)
    """
    return await baixar_e_analisar_recurso_sp(id_recurso, max_linhas, max_tamanho_mb)


@mcp.tool()
async def sp_listar_organizacoes() -> str:
    """
    Lista todas as organizações (órgãos e entidades) disponíveis no Portal SP.

    Retorna a lista de organizações com seus respectivos slugs para uso em outras ferramentas.
    """
    return await listar_organizacoes_sp()


@mcp.tool()
async def sp_listar_grupos() -> str:
    """
    Lista todos os grupos temáticos disponíveis no Portal SP.

    Retorna categorias como Saúde, Educação, Transporte, Segurança Pública, etc.
    """
    return await listar_grupos_sp()


# ──────────────────────────────────────────────────────────────────────────────
# Ferramentas: Portal Federal de Dados Abertos (dados.gov.br)
# ──────────────────────────────────────────────────────────────────────────────


@mcp.tool()
async def federal_buscar_conjuntos(
    consulta: str,
    pagina: int = 1,
    tamanho_pagina: int = 20,
) -> str:
    """
    Pesquisa conjuntos de dados no Portal Federal de Dados Abertos (dados.gov.br).

    Retorna conjuntos de dados com metadados (título, descrição, organização, tags, quantidade de recursos).

    Args:
        consulta: Termos de pesquisa (ex.: "licitacoes", "servidores publicos", "orçamento")
        pagina: Número da página (padrão: 1)
        tamanho_pagina: Quantidade de resultados por página (padrão: 20, máximo: 100)
    """
    return await buscar_conjuntos_federal(consulta, pagina, tamanho_pagina)


@mcp.tool()
async def federal_detalhes_conjunto(
    id_conjunto: str,
) -> str:
    """
    Obtém informações detalhadas sobre um conjunto de dados específico do Portal Federal.

    Retorna metadados completos: título, descrição, organização, tags, datas, licença, etc.

    Args:
        id_conjunto: ID ou slug do conjunto de dados
    """
    return await detalhes_conjunto_federal(id_conjunto)


@mcp.tool()
async def federal_listar_recursos(
    id_conjunto: str,
) -> str:
    """
    Lista todos os recursos (arquivos) disponíveis em um conjunto de dados do Portal Federal.

    Retorna metadados de cada recurso: formato, tamanho, tipo, URL de download.

    Args:
        id_conjunto: ID ou slug do conjunto de dados
    """
    return await listar_recursos_federal(id_conjunto)


@mcp.tool()
async def federal_detalhes_recurso(
    id_recurso: str,
) -> str:
    """
    Obtém informações detalhadas sobre um recurso (arquivo) específico do Portal Federal.

    Retorna formato, tamanho, tipo MIME, URL de download e conjunto de dados associado.

    Args:
        id_recurso: ID UUID do recurso
    """
    return await detalhes_recurso_federal(id_recurso)


@mcp.tool()
async def federal_baixar_e_analisar_recurso(
    id_recurso: str,
    max_linhas: int = 20,
    max_tamanho_mb: int = 500,
) -> str:
    """
    Faz o download e analisa o conteúdo de um recurso do Portal Federal.

    Suporta os formatos: CSV, CSV.GZ, JSON, JSONL, XLSX, XLS.
    Útil para visualizar amostras dos dados sem baixar o arquivo completo.

    Args:
        id_recurso: ID UUID do recurso
        max_linhas: Número máximo de linhas a retornar (padrão: 20)
        max_tamanho_mb: Tamanho máximo do arquivo em MB (padrão: 500)
    """
    return await baixar_e_analisar_recurso_federal(
        id_recurso, max_linhas, max_tamanho_mb
    )


@mcp.tool()
async def federal_listar_organizacoes(
    pagina: int = 1,
    tamanho_pagina: int = 50,
) -> str:
    """
    Lista organizações (ministérios, autarquias, fundações) disponíveis no Portal Federal.

    Args:
        pagina: Número da página (padrão: 1)
        tamanho_pagina: Quantidade de resultados por página (padrão: 50)
    """
    return await listar_organizacoes_federal(pagina, tamanho_pagina)


@mcp.tool()
async def federal_listar_temas() -> str:
    """
    Lista todos os temas/grupos disponíveis no Portal Federal de Dados Abertos.

    Retorna categorias temáticas como Agricultura, Ciência, Educação, Saúde, etc.
    """
    return await listar_temas_federal()


# ──────────────────────────────────────────────────────────────────────────────
# Inicialização do servidor
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("MCP_PORT", "8000"))
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
    )
