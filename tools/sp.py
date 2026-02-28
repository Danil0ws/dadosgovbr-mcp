"""
Ferramentas para o Portal de Dados Abertos do Estado de São Paulo.

Portal: https://dadosabertos.sp.gov.br
API: CKAN 2.x (https://dadosabertos.sp.gov.br/api/3/action/)
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

# URL base da API CKAN do Portal SP
BASE_URL_SP = "https://dadosabertos.sp.gov.br/api/3/action"


async def _ckan_action(action: str, params: dict[str, Any] | None = None) -> Any:
    """
    Chama uma action da API CKAN do Portal SP.

    Args:
        action: Nome da action CKAN (ex.: "package_search")
        params: Parâmetros da requisição

    Returns:
        Dados do campo "result" da resposta CKAN

    Raises:
        ValueError: Se a API retornar erro
    """
    url = f"{BASE_URL_SP}/{action}"
    resposta = await requisicao_get(url, params=params)

    if not isinstance(resposta, dict):
        raise ValueError(f"Resposta inesperada da API CKAN SP: {type(resposta)}")

    if not resposta.get("success"):
        erro = resposta.get("error", {})
        mensagem = (
            erro.get("message", str(erro)) if isinstance(erro, dict) else str(erro)
        )
        raise ValueError(f"Erro da API CKAN SP ({action}): {mensagem}")

    return resposta.get("result", {})


async def buscar_conjuntos_sp(
    consulta: str,
    pagina: int = 1,
    tamanho_pagina: int = 20,
) -> str:
    """
    Pesquisa conjuntos de dados no Portal SP via CKAN.

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
        resultado = await _ckan_action(
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

        return formatar_lista_conjuntos(conjuntos, total, pagina, tamanho_pagina)

    except Exception as erro:  # noqa: BLE001
        return f"Erro ao pesquisar conjuntos no Portal SP: {erro}"


async def detalhes_conjunto_sp(id_conjunto: str) -> str:
    """
    Obtém detalhes de um conjunto de dados do Portal SP.

    Args:
        id_conjunto: ID ou slug do conjunto de dados

    Returns:
        Texto formatado com os metadados do conjunto
    """
    try:
        resultado = await _ckan_action("package_show", params={"id": id_conjunto})
        return formatar_conjunto(resultado)
    except Exception as erro:  # noqa: BLE001
        return (
            f"Erro ao obter detalhes do conjunto '{id_conjunto}' no Portal SP: {erro}"
        )


async def listar_recursos_sp(id_conjunto: str) -> str:
    """
    Lista os recursos de um conjunto de dados do Portal SP.

    Args:
        id_conjunto: ID ou slug do conjunto de dados

    Returns:
        Texto formatado com a lista de recursos
    """
    try:
        resultado = await _ckan_action("package_show", params={"id": id_conjunto})
        recursos = resultado.get("resources", [])
        return formatar_lista_recursos(recursos)
    except Exception as erro:  # noqa: BLE001
        return (
            f"Erro ao listar recursos do conjunto '{id_conjunto}' no Portal SP: {erro}"
        )


async def detalhes_recurso_sp(id_recurso: str) -> str:
    """
    Obtém detalhes de um recurso do Portal SP.

    Args:
        id_recurso: ID UUID do recurso

    Returns:
        Texto formatado com os metadados do recurso
    """
    try:
        resultado = await _ckan_action("resource_show", params={"id": id_recurso})
        return formatar_recurso(resultado)
    except Exception as erro:  # noqa: BLE001
        return f"Erro ao obter detalhes do recurso '{id_recurso}' no Portal SP: {erro}"


async def baixar_e_analisar_recurso_sp(
    id_recurso: str,
    max_linhas: int = 20,
    max_tamanho_mb: int = 500,
) -> str:
    """
    Faz download e analisa um recurso do Portal SP.

    Args:
        id_recurso: ID UUID do recurso
        max_linhas: Número máximo de linhas/itens a retornar
        max_tamanho_mb: Tamanho máximo do arquivo em MB

    Returns:
        Texto formatado com a análise do recurso
    """
    try:
        # Primeiro obter metadados para pegar a URL
        recurso = await _ckan_action("resource_show", params={"id": id_recurso})
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
        return f"Erro ao baixar e analisar recurso '{id_recurso}' do Portal SP: {erro}"


async def listar_organizacoes_sp() -> str:
    """
    Lista todas as organizações do Portal SP.

    Returns:
        Texto formatado com a lista de organizações
    """
    try:
        resultado = await _ckan_action(
            "organization_list", params={"all_fields": True, "limit": 200}
        )

        if isinstance(resultado, list):
            if resultado and isinstance(resultado[0], str):
                # Retornou apenas slugs
                return "Organizações disponíveis:\n" + "\n".join(
                    f"- {slug}" for slug in resultado
                )
            else:
                # Retornou objetos completos
                linhas = ["Organizações disponíveis:\n" + "=" * 60]
                for org in resultado:
                    if not isinstance(org, dict):
                        continue
                    nome = org.get("title", org.get("name", "N/A"))
                    slug = org.get("name", "N/A")
                    num_packages = org.get("package_count", 0)
                    linhas.append(
                        f"**{nome}** (slug: {slug}) — {num_packages} conjuntos"
                    )
                return "\n".join(linhas)

        return formatar_json(resultado)

    except Exception as erro:  # noqa: BLE001
        return f"Erro ao listar organizações do Portal SP: {erro}"


async def listar_grupos_sp() -> str:
    """
    Lista todos os grupos temáticos do Portal SP.

    Returns:
        Texto formatado com a lista de grupos
    """
    try:
        resultado = await _ckan_action("group_list", params={"all_fields": True})

        if isinstance(resultado, list):
            if resultado and isinstance(resultado[0], str):
                return "Grupos temáticos disponíveis:\n" + "\n".join(
                    f"- {slug}" for slug in resultado
                )
            else:
                linhas = ["Grupos temáticos disponíveis:\n" + "=" * 60]
                for grupo in resultado:
                    nome = grupo.get(
                        "display_name", grupo.get("title", grupo.get("name", "N/A"))
                    )
                    slug = grupo.get("name", "N/A")
                    num_packages = grupo.get("package_count", 0)
                    linhas.append(
                        f"**{nome}** (slug: {slug}) — {num_packages} conjuntos"
                    )
                return "\n".join(linhas)

        return formatar_json(resultado)

    except Exception as erro:  # noqa: BLE001
        return f"Erro ao listar grupos do Portal SP: {erro}"
