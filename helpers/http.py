"""
Cliente HTTP assíncrono para comunicação com as APIs dos portais de dados abertos.

Utiliza httpx para requisições HTTP com suporte a timeouts e retry automático.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Timeout padrão para requisições (em segundos)
TIMEOUT_PADRAO = 30.0
TIMEOUT_DOWNLOAD = 120.0

# Headers padrão para todas as requisições
HEADERS_PADRAO = {
    "Accept": "application/json",
    "User-Agent": "dadosgovbr-mcp/1.0 (https://github.com/seu-usuario/dadosgovbr-mcp)",
}

# Número de tentativas em caso de falha
MAX_TENTATIVAS = 3
ESPERA_ENTRE_TENTATIVAS = 1.0  # segundos


async def requisicao_get(
    url: str,
    params: dict[str, Any] | None = None,
    timeout: float = TIMEOUT_PADRAO,
    headers: dict[str, str] | None = None,
) -> dict[str, Any] | list[Any]:
    """
    Realiza uma requisição GET assíncrona e retorna o JSON da resposta.

    Args:
        url: URL completa da requisição
        params: Parâmetros de query string (opcional)
        timeout: Timeout em segundos (padrão: 30)
        headers: Headers adicionais (opcional)

    Returns:
        Dados JSON da resposta (dict ou list)

    Raises:
        httpx.HTTPStatusError: Em caso de erro HTTP (4xx, 5xx)
        httpx.TimeoutException: Em caso de timeout
        ValueError: Em caso de resposta não-JSON
    """
    headers_completos = {**HEADERS_PADRAO, **(headers or {})}

    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            async with httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=True,
            ) as cliente:
                resposta = await cliente.get(
                    url,
                    params=params,
                    headers=headers_completos,
                )
                resposta.raise_for_status()
                return resposta.json()

        except httpx.HTTPStatusError as erro:
            if erro.response.status_code < 500 or tentativa == MAX_TENTATIVAS:
                raise
            logger.warning(
                "Tentativa %d/%d falhou para %s: HTTP %d. Tentando novamente...",
                tentativa,
                MAX_TENTATIVAS,
                url,
                erro.response.status_code,
            )
            await asyncio.sleep(ESPERA_ENTRE_TENTATIVAS * tentativa)

        except httpx.TimeoutException:
            if tentativa == MAX_TENTATIVAS:
                raise
            logger.warning(
                "Tentativa %d/%d falhou para %s: timeout. Tentando novamente...",
                tentativa,
                MAX_TENTATIVAS,
                url,
            )
            await asyncio.sleep(ESPERA_ENTRE_TENTATIVAS * tentativa)

    # Nunca deve chegar aqui, mas satisfaz o type checker
    raise RuntimeError(f"Falha após {MAX_TENTATIVAS} tentativas para {url}")


async def baixar_bytes(
    url: str,
    max_tamanho_mb: int = 500,
    timeout: float = TIMEOUT_DOWNLOAD,
) -> tuple[bytes, str]:
    """
    Faz o download de um arquivo como bytes.

    Args:
        url: URL do arquivo
        max_tamanho_mb: Tamanho máximo permitido em MB
        timeout: Timeout em segundos (padrão: 120)

    Returns:
        Tupla (conteúdo_bytes, content_type)

    Raises:
        ValueError: Se o arquivo exceder o tamanho máximo
        httpx.HTTPStatusError: Em caso de erro HTTP
    """
    max_tamanho_bytes = max_tamanho_mb * 1024 * 1024

    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
    ) as cliente:
        async with cliente.stream("GET", url, headers=HEADERS_PADRAO) as resposta:
            resposta.raise_for_status()

            content_type = resposta.headers.get("content-type", "")

            # Verificar tamanho pelo Content-Length antes de baixar
            content_length = resposta.headers.get("content-length")
            if content_length and int(content_length) > max_tamanho_bytes:
                raise ValueError(
                    f"Arquivo muito grande: {int(content_length) / 1024 / 1024:.1f} MB "
                    f"(máximo: {max_tamanho_mb} MB)"
                )

            conteudo = b""
            async for chunk in resposta.aiter_bytes(chunk_size=8192):
                conteudo += chunk
                if len(conteudo) > max_tamanho_bytes:
                    raise ValueError(
                        f"Arquivo excedeu o tamanho máximo de {max_tamanho_mb} MB durante o download"
                    )

    return conteudo, content_type
