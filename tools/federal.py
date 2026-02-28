"""
Ferramentas para o Portal Federal de Dados Abertos (dados.gov.br).

Portal: https://dados.gov.br
API: CKAN 2.x (https://dados.gov.br/dados/api/3/action/) - requer autenticação para alguns endpoints
API Pública: https://dados.gov.br/dados/api/publico/

Nota: O portal federal usa uma plataforma customizada. Para busca e listagem,
utilizamos a API pública disponível. Para download de recursos, acessamos
diretamente as URLs dos arquivos.
"""

from __future__ import annotations

import logging
from typing import Any

from helpers.formatter import (
    formatar_analise_recurso,
    formatar_conjunto,
    formatar_json,
    formatar_lista_conjuntos,
    formatar_lista_recursos,
    formatar_recurso,
)
from helpers.http import baixar_bytes, requisicao_get
from helpers.parser import analisar_conteudo

logger = logging.getLogger(__name__)

# URL base da API CKAN do Portal Federal
# O portal federal também expõe uma API CKAN pública
BASE_URL_FEDERAL_CKAN = "https://dados.gov.br/dados/api/3/action"

# Headers especiais para contornar proteções do portal federal
HEADERS_FEDERAL = {
    "Accept": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (compatible; dadosgovbr-mcp/1.0; "
        "+https://github.com/seu-usuario/dadosgovbr-mcp)"
    ),
    "Referer": "https://dados.gov.br/",
}


async def _ckan_action_federal(
    action: str,
    params: dict[str, Any] | None = None,
) -> Any:
    """
    Chama uma action da API CKAN do Portal Federal.

    O portal federal exige navegação autenticada para sua interface,
    mas expõe uma API CKAN pública para acesso programático.

    Args:
        action: Nome da action CKAN (ex.: "package_search")
        params: Parâmetros da requisição

    Returns:
        Dados do campo "result" da resposta CKAN

    Raises:
        ValueError: Se a API retornar erro
    """
    url = f"{BASE_URL_FEDERAL_CKAN}/{action}"

    try:
        resposta = await requisicao_get(url, params=params, headers=HEADERS_FEDERAL)
    except Exception as erro:
        # Se a API CKAN principal falhar, tentar endpoint alternativo
        logger.warning(
            "API CKAN federal falhou para %s: %s. Tentando fallback...", action, erro
        )
        raise

    if not isinstance(resposta, dict):
        raise ValueError(f"Resposta inesperada da API CKAN Federal: {type(resposta)}")

    if not resposta.get("success"):
        erro = resposta.get("error", {})
        mensagem = (
            erro.get("message", str(erro)) if isinstance(erro, dict) else str(erro)
        )
        raise ValueError(f"Erro da API CKAN Federal ({action}): {mensagem}")

    return resposta.get("result", {})


async def buscar_conjuntos_federal(
    consulta: str,
    pagina: int = 1,
    tamanho_pagina: int = 20,
) -> str:
    """
    Pesquisa conjuntos de dados no Portal Federal.

    Args:
        consulta: Termos de pesquisa
        pagina: Número da página (1-indexed)
        tamanho_pagina: Itens por página (máximo 100)

    Returns:
        Texto formatado com os resultados da pesquisa
    """
    tamanho_pagina = min(tamanho_pagina, 100)
    start = (pagina - 1) * tamanho_pagina

    try:
        resultado = await _ckan_action_federal(
            "package_search",
            params={
                "q": consulta,
                "rows": tamanho_pagina,
                "start": start,
                "sort": "score desc, metadata_modified desc",
            },
        )

        conjuntos = resultado.get("results", [])
        total = resultado.get("count", 0)

        if not conjuntos and total == 0:
            return (
                f"Nenhum resultado encontrado para '{consulta}' no Portal Federal.\n\n"
                "Nota: O Portal Federal de Dados Abertos (dados.gov.br) pode exigir "
                "autenticação para acesso à API. Tente utilizar o Portal SP "
                "(dadosabertos.sp.gov.br) ou acesse diretamente https://dados.gov.br"
            )

        return formatar_lista_conjuntos(conjuntos, total, pagina, tamanho_pagina)

    except Exception as erro:  # noqa: BLE001
        return (
            f"Erro ao pesquisar conjuntos no Portal Federal: {erro}\n\n"
            "Nota: O Portal Federal (dados.gov.br) pode exigir autenticação. "
            "Para dados federais públicos, considere usar as APIs do Portal SP "
            "ou acessar diretamente https://dados.gov.br"
        )


async def detalhes_conjunto_federal(id_conjunto: str) -> str:
    """
    Obtém detalhes de um conjunto de dados do Portal Federal.

    Args:
        id_conjunto: ID ou slug do conjunto de dados

    Returns:
        Texto formatado com os metadados do conjunto
    """
    try:
        resultado = await _ckan_action_federal(
            "package_show", params={"id": id_conjunto}
        )
        return formatar_conjunto(resultado)
    except Exception as erro:  # noqa: BLE001
        return f"Erro ao obter detalhes do conjunto '{id_conjunto}' no Portal Federal: {erro}"


async def listar_recursos_federal(id_conjunto: str) -> str:
    """
    Lista os recursos de um conjunto de dados do Portal Federal.

    Args:
        id_conjunto: ID ou slug do conjunto de dados

    Returns:
        Texto formatado com a lista de recursos
    """
    try:
        resultado = await _ckan_action_federal(
            "package_show", params={"id": id_conjunto}
        )
        recursos = resultado.get("resources", [])
        return formatar_lista_recursos(recursos)
    except Exception as erro:  # noqa: BLE001
        return f"Erro ao listar recursos do conjunto '{id_conjunto}' no Portal Federal: {erro}"


async def detalhes_recurso_federal(id_recurso: str) -> str:
    """
    Obtém detalhes de um recurso do Portal Federal.

    Args:
        id_recurso: ID UUID do recurso

    Returns:
        Texto formatado com os metadados do recurso
    """
    try:
        resultado = await _ckan_action_federal(
            "resource_show", params={"id": id_recurso}
        )
        return formatar_recurso(resultado)
    except Exception as erro:  # noqa: BLE001
        return f"Erro ao obter detalhes do recurso '{id_recurso}' no Portal Federal: {erro}"


async def baixar_e_analisar_recurso_federal(
    id_recurso: str,
    max_linhas: int = 20,
    max_tamanho_mb: int = 500,
) -> str:
    """
    Faz download e analisa um recurso do Portal Federal.

    Args:
        id_recurso: ID UUID do recurso
        max_linhas: Número máximo de linhas/itens a retornar
        max_tamanho_mb: Tamanho máximo do arquivo em MB

    Returns:
        Texto formatado com a análise do recurso
    """
    try:
        # Primeiro obter metadados para pegar a URL
        recurso = await _ckan_action_federal("resource_show", params={"id": id_recurso})
        url = recurso.get("url", "")

        if not url:
            return f"Erro: Recurso '{id_recurso}' não possui URL de download."

        # Fazer o download
        conteudo, content_type = await baixar_bytes(url, max_tamanho_mb=max_tamanho_mb)

        # Analisar o conteúdo
        dados = analisar_conteudo(conteudo, url, content_type, max_linhas=max_linhas)

        cabecalho = (
            f"Recurso: {recurso.get('name', id_recurso)}\n"
            f"URL: {url}\n"
            f"Tamanho baixado: {len(conteudo) / 1024:.1f} KB\n" + "=" * 60 + "\n"
        )

        return cabecalho + formatar_analise_recurso(dados)

    except ValueError as erro:
        return f"Erro de validação ao analisar recurso '{id_recurso}': {erro}"
    except Exception as erro:  # noqa: BLE001
        return f"Erro ao baixar e analisar recurso '{id_recurso}' do Portal Federal: {erro}"


async def listar_organizacoes_federal(
    pagina: int = 1,
    tamanho_pagina: int = 50,
) -> str:
    """
    Lista organizações do Portal Federal.

    Args:
        pagina: Número da página
        tamanho_pagina: Itens por página

    Returns:
        Texto formatado com a lista de organizações
    """
    try:
        tamanho_pagina = min(tamanho_pagina, 100)
        offset = (pagina - 1) * tamanho_pagina

        resultado = await _ckan_action_federal(
            "organization_list",
            params={
                "all_fields": True,
                "limit": tamanho_pagina,
                "offset": offset,
                "include_dataset_count": True,
            },
        )

        if isinstance(resultado, list):
            if not resultado:
                return "Nenhuma organização encontrada."

            if isinstance(resultado[0], str):
                return "Organizações disponíveis:\n" + "\n".join(
                    f"- {slug}" for slug in resultado
                )

            linhas = [f"Organizações (página {pagina}):\n" + "=" * 60]
            for org in resultado:
                nome = org.get("title", org.get("name", "N/A"))
                slug = org.get("name", "N/A")
                num_packages = org.get("package_count", 0)
                linhas.append(f"**{nome}** (slug: {slug}) — {num_packages} conjuntos")
            return "\n".join(linhas)

        return formatar_json(resultado)

    except Exception as erro:  # noqa: BLE001
        return f"Erro ao listar organizações do Portal Federal: {erro}"


async def listar_temas_federal() -> str:
    """
    Lista todos os temas/grupos do Portal Federal.

    Returns:
        Texto formatado com a lista de temas
    """
    try:
        resultado = await _ckan_action_federal(
            "group_list",
            params={"all_fields": True},
        )

        if isinstance(resultado, list):
            if not resultado:
                return "Nenhum tema encontrado."

            if isinstance(resultado[0], str):
                return "Temas disponíveis:\n" + "\n".join(
                    f"- {slug}" for slug in resultado
                )

            linhas = ["Temas disponíveis:\n" + "=" * 60]
            for grupo in resultado:
                nome = grupo.get(
                    "display_name", grupo.get("title", grupo.get("name", "N/A"))
                )
                slug = grupo.get("name", "N/A")
                num_packages = grupo.get("package_count", 0)
                linhas.append(f"**{nome}** (slug: {slug}) — {num_packages} conjuntos")
            return "\n".join(linhas)

        return formatar_json(resultado)

    except Exception as erro:  # noqa: BLE001
        return f"Erro ao listar temas do Portal Federal: {erro}"
