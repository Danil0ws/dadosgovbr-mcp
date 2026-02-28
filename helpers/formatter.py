"""
Utilitários para formatação de respostas para o MCP.

Funções para converter dados JSON das APIs em texto legível e estruturado.
"""

from __future__ import annotations

import json
from typing import Any


def formatar_json(dados: Any, indentacao: int = 2) -> str:
    """
    Serializa dados Python para JSON formatado.

    Args:
        dados: Dados a serializar
        indentacao: Nível de indentação (padrão: 2)

    Returns:
        String JSON formatada
    """
    return json.dumps(dados, ensure_ascii=False, indent=indentacao)


def formatar_conjunto(conjunto: dict[str, Any]) -> str:
    """
    Formata metadados de um conjunto de dados para exibição legível.

    Args:
        conjunto: Dicionário com metadados do conjunto

    Returns:
        Texto formatado com as informações do conjunto
    """
    linhas = [
        f"**{conjunto.get('title', 'Sem título')}**",
        f"ID: {conjunto.get('id', 'N/A')}",
        f"Slug: {conjunto.get('name', 'N/A')}",
    ]

    if conjunto.get("notes"):
        descricao = conjunto["notes"][:300]
        if len(conjunto["notes"]) > 300:
            descricao += "..."
        linhas.append(f"Descrição: {descricao}")

    if conjunto.get("organization"):
        org = conjunto["organization"]
        linhas.append(f"Organização: {org.get('title', org.get('name', 'N/A'))}")

    if conjunto.get("tags"):
        tags = [t.get("display_name", t.get("name", "")) for t in conjunto["tags"]]
        linhas.append(f"Tags: {', '.join(tags)}")

    if conjunto.get("license_title"):
        linhas.append(f"Licença: {conjunto['license_title']}")

    if conjunto.get("metadata_created"):
        linhas.append(f"Criado em: {conjunto['metadata_created'][:10]}")

    if conjunto.get("metadata_modified"):
        linhas.append(f"Atualizado em: {conjunto['metadata_modified'][:10]}")

    num_recursos = conjunto.get("num_resources", len(conjunto.get("resources", [])))
    linhas.append(f"Recursos: {num_recursos}")

    return "\n".join(linhas)


def formatar_lista_conjuntos(
    conjuntos: list[dict[str, Any]],
    total: int,
    pagina: int,
    tamanho_pagina: int,
) -> str:
    """
    Formata uma lista de conjuntos de dados para exibição.

    Args:
        conjuntos: Lista de conjuntos de dados
        total: Total de resultados encontrados
        pagina: Página atual
        tamanho_pagina: Tamanho da página

    Returns:
        Texto formatado com a lista de conjuntos
    """
    if not conjuntos:
        return "Nenhum conjunto de dados encontrado."

    inicio = (pagina - 1) * tamanho_pagina + 1
    fim = min(inicio + len(conjuntos) - 1, total)
    total_paginas = (total + tamanho_pagina - 1) // tamanho_pagina

    cabecalho = (
        f"Resultados {inicio}-{fim} de {total} conjuntos "
        f"(página {pagina}/{total_paginas})\n" + "=" * 60
    )

    itens = []
    for i, conjunto in enumerate(conjuntos, start=inicio):
        titulo = conjunto.get("title", "Sem título")
        id_conjunto = conjunto.get("id", conjunto.get("name", "N/A"))
        num_recursos = conjunto.get("num_resources", len(conjunto.get("resources", [])))
        org = ""
        if conjunto.get("organization"):
            org_data = conjunto["organization"]
            org = f" | {org_data.get('title', org_data.get('name', ''))}"

        notas = ""
        if conjunto.get("notes"):
            notas = f"\n   {conjunto['notes'][:120].replace(chr(10), ' ')}..."

        itens.append(
            f"{i}. **{titulo}**\n   ID: {id_conjunto} | Recursos: {num_recursos}{org}{notas}"
        )

    return cabecalho + "\n\n" + "\n\n".join(itens)


def formatar_recurso(recurso: dict[str, Any]) -> str:
    """
    Formata metadados de um recurso para exibição legível.

    Args:
        recurso: Dicionário com metadados do recurso

    Returns:
        Texto formatado com as informações do recurso
    """
    linhas = [
        f"**{recurso.get('name', 'Sem nome')}**",
        f"ID: {recurso.get('id', 'N/A')}",
        f"Formato: {recurso.get('format', 'Desconhecido') or 'Desconhecido'}",
    ]

    if recurso.get("description"):
        descricao = recurso["description"][:200]
        if len(recurso["description"]) > 200:
            descricao += "..."
        linhas.append(f"Descrição: {descricao}")

    if recurso.get("url"):
        linhas.append(f"URL: {recurso['url']}")

    if recurso.get("size"):
        tamanho_mb = recurso["size"] / 1024 / 1024
        linhas.append(f"Tamanho: {tamanho_mb:.2f} MB")

    if recurso.get("mimetype"):
        linhas.append(f"Tipo MIME: {recurso['mimetype']}")

    if recurso.get("created"):
        linhas.append(f"Criado em: {recurso['created'][:10]}")

    if recurso.get("last_modified"):
        linhas.append(f"Modificado em: {recurso['last_modified'][:10]}")

    return "\n".join(linhas)


def formatar_lista_recursos(recursos: list[dict[str, Any]]) -> str:
    """
    Formata uma lista de recursos para exibição.

    Args:
        recursos: Lista de recursos

    Returns:
        Texto formatado com a lista de recursos
    """
    if not recursos:
        return "Nenhum recurso encontrado neste conjunto de dados."

    cabecalho = f"Total: {len(recursos)} recurso(s)\n" + "=" * 60

    itens = []
    for i, recurso in enumerate(recursos, start=1):
        nome = recurso.get("name", "Sem nome")
        id_recurso = recurso.get("id", "N/A")
        formato = recurso.get("format", "?") or "?"
        url = recurso.get("url", "")

        tamanho = ""
        if recurso.get("size"):
            tamanho_mb = recurso["size"] / 1024 / 1024
            tamanho = f" | {tamanho_mb:.1f} MB"

        itens.append(
            f"{i}. **{nome}**\n"
            f"   ID: {id_recurso} | Formato: {formato}{tamanho}\n"
            f"   URL: {url}"
        )

    return cabecalho + "\n\n" + "\n\n".join(itens)


def formatar_analise_recurso(dados: dict[str, Any]) -> str:
    """
    Formata o resultado da análise de um recurso para exibição.

    Args:
        dados: Resultado do parsing do arquivo

    Returns:
        Texto formatado com os dados analisados
    """
    if "erro" in dados:
        return f"Erro na análise: {dados['erro']}"

    formato = dados.get("formato", "Desconhecido")
    linhas = [f"Formato: {formato}"]

    if "colunas" in dados:
        linhas.append(
            f"Colunas ({len(dados['colunas'])}): {', '.join(dados['colunas'])}"
        )

    if "total_linhas_lidas" in dados:
        linhas.append(f"Total de linhas: {dados['total_linhas_lidas']}")
        linhas.append(f"Linhas exibidas: {dados['linhas_exibidas']}")

    if "total_itens" in dados:
        linhas.append(f"Total de itens: {dados['total_itens']}")
        linhas.append(f"Itens exibidos: {dados['itens_exibidos']}")

    if "total_linhas" in dados:
        linhas.append(f"Total de linhas: {dados['total_linhas']}")
        linhas.append(f"Linhas exibidas: {dados['linhas_exibidas']}")

    linhas.append("\n--- Dados ---")
    linhas.append(json.dumps(dados.get("dados", []), ensure_ascii=False, indent=2))

    return "\n".join(linhas)
