"""
Utilitários para parsing e análise de arquivos de dados.

Suporta os formatos: CSV, CSV.GZ, JSON, JSONL, XLSX, XLS.
"""

from __future__ import annotations

import csv
import gzip
import io
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def detectar_formato(url: str, content_type: str = "") -> str:
    """
    Detecta o formato de um arquivo baseado na URL e no content-type.

    Args:
        url: URL do arquivo
        content_type: Content-Type da resposta HTTP

    Returns:
        Formato detectado em minúsculas (ex.: "csv", "json", "xlsx")
    """
    url_lower = url.lower().split("?")[0]

    if url_lower.endswith(".csv.gz"):
        return "csv.gz"
    if url_lower.endswith(".csv"):
        return "csv"
    if url_lower.endswith(".jsonl") or url_lower.endswith(".ndjson"):
        return "jsonl"
    if url_lower.endswith(".json"):
        return "json"
    if url_lower.endswith(".xlsx"):
        return "xlsx"
    if url_lower.endswith(".xls"):
        return "xls"

    # Detectar pelo content-type
    ct_lower = content_type.lower()
    if "csv" in ct_lower:
        return "csv"
    if "json" in ct_lower:
        return "json"
    if "spreadsheet" in ct_lower or "excel" in ct_lower:
        return "xlsx"

    return "desconhecido"


def analisar_csv(conteudo: bytes, max_linhas: int = 20) -> dict[str, Any]:
    """
    Analisa um arquivo CSV e retorna os dados estruturados.

    Args:
        conteudo: Conteúdo do arquivo em bytes
        max_linhas: Número máximo de linhas de dados a retornar

    Returns:
        Dicionário com colunas, linhas e metadados
    """
    # Tentar diferentes encodings
    texto = None
    for encoding in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            texto = conteudo.decode(encoding)
            break
        except UnicodeDecodeError:
            continue

    if texto is None:
        return {"erro": "Não foi possível decodificar o arquivo CSV"}

    # Detectar delimitador
    amostra = texto[:4096]
    dialect = csv.Sniffer().sniff(amostra, delimiters=",;\t|")

    leitor = csv.DictReader(io.StringIO(texto), dialect=dialect)

    colunas = leitor.fieldnames or []
    linhas = []
    total_lido = 0

    for linha in leitor:
        total_lido += 1
        if len(linhas) < max_linhas:
            linhas.append(dict(linha))

    return {
        "formato": "CSV",
        "colunas": list(colunas),
        "total_linhas_lidas": total_lido,
        "linhas_exibidas": len(linhas),
        "dados": linhas,
    }


def analisar_csv_gz(conteudo: bytes, max_linhas: int = 20) -> dict[str, Any]:
    """
    Analisa um arquivo CSV comprimido com gzip.

    Args:
        conteudo: Conteúdo do arquivo comprimido em bytes
        max_linhas: Número máximo de linhas de dados a retornar

    Returns:
        Dicionário com colunas, linhas e metadados
    """
    try:
        conteudo_descomprimido = gzip.decompress(conteudo)
        resultado = analisar_csv(conteudo_descomprimido, max_linhas)
        resultado["formato"] = "CSV.GZ"
        return resultado
    except OSError as erro:
        return {"erro": f"Falha ao descomprimir arquivo GZ: {erro}"}


def analisar_json(conteudo: bytes, max_linhas: int = 20) -> dict[str, Any]:
    """
    Analisa um arquivo JSON e retorna os dados estruturados.

    Suporta arrays JSON no nível raiz e objetos com chave de lista.

    Args:
        conteudo: Conteúdo do arquivo em bytes
        max_linhas: Número máximo de itens a retornar

    Returns:
        Dicionário com estrutura e amostra dos dados
    """
    try:
        texto = conteudo.decode("utf-8")
        dados = json.loads(texto)
    except (UnicodeDecodeError, json.JSONDecodeError) as erro:
        return {"erro": f"Falha ao analisar JSON: {erro}"}

    # Se for uma lista direta
    if isinstance(dados, list):
        return {
            "formato": "JSON",
            "tipo_raiz": "array",
            "total_itens": len(dados),
            "itens_exibidos": min(max_linhas, len(dados)),
            "dados": dados[:max_linhas],
        }

    # Se for um objeto, procurar a primeira lista
    if isinstance(dados, dict):
        for chave, valor in dados.items():
            if isinstance(valor, list):
                return {
                    "formato": "JSON",
                    "tipo_raiz": "objeto",
                    "chave_dados": chave,
                    "total_itens": len(valor),
                    "itens_exibidos": min(max_linhas, len(valor)),
                    "dados": valor[:max_linhas],
                    "outras_chaves": [k for k in dados if k != chave],
                }

        return {
            "formato": "JSON",
            "tipo_raiz": "objeto",
            "dados": dados,
        }

    return {"formato": "JSON", "dados": dados}


def analisar_jsonl(conteudo: bytes, max_linhas: int = 20) -> dict[str, Any]:
    """
    Analisa um arquivo JSONL (JSON Lines) e retorna os dados estruturados.

    Args:
        conteudo: Conteúdo do arquivo em bytes
        max_linhas: Número máximo de linhas a retornar

    Returns:
        Dicionário com estrutura e amostra dos dados
    """
    try:
        texto = conteudo.decode("utf-8")
    except UnicodeDecodeError:
        texto = conteudo.decode("latin-1")

    linhas = []
    total = 0

    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha:
            continue
        total += 1
        if len(linhas) < max_linhas:
            try:
                linhas.append(json.loads(linha))
            except json.JSONDecodeError:
                linhas.append({"_linha_invalida": linha})

    return {
        "formato": "JSONL",
        "total_linhas": total,
        "linhas_exibidas": len(linhas),
        "dados": linhas,
    }


def analisar_xlsx(conteudo: bytes, max_linhas: int = 20) -> dict[str, Any]:
    """
    Analisa um arquivo XLSX/XLS e retorna os dados estruturados.

    Args:
        conteudo: Conteúdo do arquivo em bytes
        max_linhas: Número máximo de linhas a retornar

    Returns:
        Dicionário com colunas, linhas e metadados
    """
    try:
        import openpyxl

        wb = openpyxl.load_workbook(
            io.BytesIO(conteudo), read_only=True, data_only=True
        )
        planilha = wb.active

        if planilha is None:
            return {"erro": "Planilha ativa não encontrada no arquivo XLSX"}

        linhas_iter = planilha.iter_rows(values_only=True)

        # Primeira linha como cabeçalho
        try:
            cabecalho = [str(c) if c is not None else "" for c in next(linhas_iter)]
        except StopIteration:
            return {"erro": "Arquivo XLSX vazio"}

        linhas = []
        total = 0

        for linha in linhas_iter:
            total += 1
            if len(linhas) < max_linhas:
                linhas.append(
                    dict(
                        zip(cabecalho, [str(v) if v is not None else "" for v in linha])
                    )
                )

        wb.close()

        return {
            "formato": "XLSX",
            "colunas": cabecalho,
            "total_linhas_lidas": total,
            "linhas_exibidas": len(linhas),
            "dados": linhas,
        }

    except ImportError:
        return {
            "erro": "Biblioteca openpyxl não disponível. Instale com: uv add openpyxl"
        }
    except Exception as erro:  # noqa: BLE001
        return {"erro": f"Falha ao analisar arquivo XLSX: {erro}"}


def analisar_conteudo(
    conteudo: bytes,
    url: str,
    content_type: str = "",
    max_linhas: int = 20,
) -> dict[str, Any]:
    """
    Detecta o formato e analisa o conteúdo de um arquivo.

    Args:
        conteudo: Conteúdo do arquivo em bytes
        url: URL original do arquivo (para detectar formato)
        content_type: Content-Type da resposta HTTP
        max_linhas: Número máximo de linhas/itens a retornar

    Returns:
        Dicionário com os dados analisados
    """
    formato = detectar_formato(url, content_type)

    analisadores = {
        "csv": analisar_csv,
        "csv.gz": analisar_csv_gz,
        "json": analisar_json,
        "jsonl": analisar_jsonl,
        "xlsx": analisar_xlsx,
        "xls": analisar_xlsx,
    }

    analisador = analisadores.get(formato)
    if analisador is None:
        return {
            "erro": (
                f"Formato '{formato}' não suportado para análise direta. "
                "Formatos suportados: CSV, CSV.GZ, JSON, JSONL, XLSX, XLS."
            )
        }

    return analisador(conteudo, max_linhas)
