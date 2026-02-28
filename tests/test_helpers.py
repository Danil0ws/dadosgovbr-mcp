"""
Testes unitários para os módulos auxiliares (helpers).

Testa parsing de arquivos, formatação e utilitários HTTP sem
necessidade de rede.
"""

import json

import pytest

from helpers.formatter import (
    formatar_analise_recurso,
    formatar_conjunto,
    formatar_lista_conjuntos,
    formatar_lista_recursos,
    formatar_recurso,
)
from helpers.parser import (
    analisar_conteudo,
    analisar_csv,
    analisar_json,
    analisar_jsonl,
    detectar_formato,
)


# ──────────────────────────────────────────────────────────────────────────────
# Testes: helpers/parser.py
# ──────────────────────────────────────────────────────────────────────────────


class TestDetectarFormato:
    """Testes para detecção de formato de arquivo."""

    def test_detecta_csv_por_url(self) -> None:
        assert detectar_formato("https://example.com/dados.csv") == "csv"

    def test_detecta_csv_gz_por_url(self) -> None:
        assert detectar_formato("https://example.com/dados.csv.gz") == "csv.gz"

    def test_detecta_json_por_url(self) -> None:
        assert detectar_formato("https://example.com/dados.json") == "json"

    def test_detecta_jsonl_por_url(self) -> None:
        assert detectar_formato("https://example.com/dados.jsonl") == "jsonl"

    def test_detecta_xlsx_por_url(self) -> None:
        assert detectar_formato("https://example.com/dados.xlsx") == "xlsx"

    def test_detecta_xls_por_url(self) -> None:
        assert detectar_formato("https://example.com/dados.xls") == "xls"

    def test_ignora_query_string(self) -> None:
        assert detectar_formato("https://example.com/dados.csv?token=abc") == "csv"

    def test_detecta_csv_por_content_type(self) -> None:
        assert detectar_formato("https://example.com/download", "text/csv") == "csv"

    def test_detecta_json_por_content_type(self) -> None:
        assert detectar_formato("https://example.com/download", "application/json") == "json"

    def test_formato_desconhecido(self) -> None:
        assert detectar_formato("https://example.com/dados.pdf") == "desconhecido"


class TestAnalisarCSV:
    """Testes para análise de arquivos CSV."""

    def test_csv_simples(self) -> None:
        csv_conteudo = b"nome,idade,cidade\nJoao,30,Sao Paulo\nMaria,25,Rio de Janeiro\n"
        resultado = analisar_csv(csv_conteudo, max_linhas=10)

        assert resultado["formato"] == "CSV"
        assert resultado["colunas"] == ["nome", "idade", "cidade"]
        assert resultado["total_linhas_lidas"] == 2
        assert len(resultado["dados"]) == 2
        assert resultado["dados"][0]["nome"] == "Joao"

    def test_csv_com_max_linhas(self) -> None:
        linhas = ["col1,col2"] + [f"val{i},val{i}" for i in range(50)]
        csv_conteudo = "\n".join(linhas).encode("utf-8")
        resultado = analisar_csv(csv_conteudo, max_linhas=10)

        assert resultado["total_linhas_lidas"] == 50
        assert resultado["linhas_exibidas"] == 10
        assert len(resultado["dados"]) == 10

    def test_csv_encoding_latin1(self) -> None:
        csv_conteudo = "nome,cidade\nJoão,São Paulo\n".encode("latin-1")
        resultado = analisar_csv(csv_conteudo)

        assert "erro" not in resultado
        assert len(resultado["dados"]) == 1

    def test_csv_ponto_e_virgula(self) -> None:
        csv_conteudo = b"nome;idade;cidade\nJoao;30;Sao Paulo\n"
        resultado = analisar_csv(csv_conteudo)

        assert "erro" not in resultado
        assert "nome" in resultado["colunas"]


class TestAnalisarJSON:
    """Testes para análise de arquivos JSON."""

    def test_json_array(self) -> None:
        dados = [{"id": 1, "nome": "Item 1"}, {"id": 2, "nome": "Item 2"}]
        conteudo = json.dumps(dados).encode("utf-8")
        resultado = analisar_json(conteudo, max_linhas=10)

        assert resultado["formato"] == "JSON"
        assert resultado["tipo_raiz"] == "array"
        assert resultado["total_itens"] == 2
        assert len(resultado["dados"]) == 2

    def test_json_objeto_com_lista(self) -> None:
        dados = {"total": 2, "resultados": [{"id": 1}, {"id": 2}]}
        conteudo = json.dumps(dados).encode("utf-8")
        resultado = analisar_json(conteudo, max_linhas=10)

        assert resultado["formato"] == "JSON"
        assert resultado["tipo_raiz"] == "objeto"
        assert resultado["chave_dados"] == "resultados"
        assert len(resultado["dados"]) == 2

    def test_json_invalido(self) -> None:
        conteudo = b"isso nao e json valido"
        resultado = analisar_json(conteudo)

        assert "erro" in resultado

    def test_json_com_max_itens(self) -> None:
        dados = [{"id": i} for i in range(100)]
        conteudo = json.dumps(dados).encode("utf-8")
        resultado = analisar_json(conteudo, max_linhas=5)

        assert resultado["total_itens"] == 100
        assert resultado["itens_exibidos"] == 5
        assert len(resultado["dados"]) == 5


class TestAnalisarJSONL:
    """Testes para análise de arquivos JSONL."""

    def test_jsonl_simples(self) -> None:
        conteudo = b'{"id": 1, "nome": "Item 1"}\n{"id": 2, "nome": "Item 2"}\n'
        resultado = analisar_jsonl(conteudo, max_linhas=10)

        assert resultado["formato"] == "JSONL"
        assert resultado["total_linhas"] == 2
        assert len(resultado["dados"]) == 2

    def test_jsonl_ignora_linhas_vazias(self) -> None:
        conteudo = b'{"id": 1}\n\n{"id": 2}\n\n'
        resultado = analisar_jsonl(conteudo, max_linhas=10)

        assert resultado["total_linhas"] == 2

    def test_jsonl_com_max_linhas(self) -> None:
        linhas = [json.dumps({"id": i}) for i in range(50)]
        conteudo = "\n".join(linhas).encode("utf-8")
        resultado = analisar_jsonl(conteudo, max_linhas=10)

        assert resultado["total_linhas"] == 50
        assert resultado["linhas_exibidas"] == 10


class TestAnalisarConteudo:
    """Testes para a função de análise automática de conteúdo."""

    def test_detecta_e_analisa_csv(self) -> None:
        conteudo = b"col1,col2\nval1,val2\n"
        resultado = analisar_conteudo(conteudo, "https://example.com/dados.csv")
        assert resultado["formato"] == "CSV"

    def test_detecta_e_analisa_json(self) -> None:
        conteudo = json.dumps([{"id": 1}]).encode()
        resultado = analisar_conteudo(conteudo, "https://example.com/dados.json")
        assert resultado["formato"] == "JSON"

    def test_formato_nao_suportado(self) -> None:
        conteudo = b"conteudo qualquer"
        resultado = analisar_conteudo(conteudo, "https://example.com/dados.pdf")
        assert "erro" in resultado


# ──────────────────────────────────────────────────────────────────────────────
# Testes: helpers/formatter.py
# ──────────────────────────────────────────────────────────────────────────────


class TestFormatar:
    """Testes para funções de formatação."""

    def test_formatar_conjunto_completo(self) -> None:
        conjunto = {
            "id": "abc-123",
            "name": "multas-pagas",
            "title": "Multas Pagas",
            "notes": "Dados de multas pagas pelo DETRAN.",
            "organization": {"title": "DETRAN-SP", "name": "detran"},
            "tags": [{"display_name": "transporte"}, {"name": "multas"}],
            "license_title": "CC BY 4.0",
            "metadata_created": "2025-01-15T10:00:00",
            "metadata_modified": "2025-06-20T08:30:00",
            "resources": [],
        }
        resultado = formatar_conjunto(conjunto)

        assert "Multas Pagas" in resultado
        assert "abc-123" in resultado
        assert "DETRAN-SP" in resultado
        assert "CC BY 4.0" in resultado

    def test_formatar_conjunto_minimo(self) -> None:
        conjunto = {"id": "xyz", "title": "Teste"}
        resultado = formatar_conjunto(conjunto)
        assert "Teste" in resultado

    def test_formatar_lista_conjuntos_vazia(self) -> None:
        resultado = formatar_lista_conjuntos([], 0, 1, 20)
        assert "Nenhum" in resultado

    def test_formatar_lista_conjuntos(self) -> None:
        conjuntos = [
            {"id": "1", "title": "Conjunto A", "name": "conjunto-a", "resources": []},
            {"id": "2", "title": "Conjunto B", "name": "conjunto-b", "resources": []},
        ]
        resultado = formatar_lista_conjuntos(conjuntos, 2, 1, 20)

        assert "Conjunto A" in resultado
        assert "Conjunto B" in resultado
        assert "2" in resultado  # total

    def test_formatar_recurso(self) -> None:
        recurso = {
            "id": "res-123",
            "name": "Arquivo CSV",
            "format": "CSV",
            "url": "https://example.com/dados.csv",
            "size": 1048576,  # 1 MB
        }
        resultado = formatar_recurso(recurso)

        assert "Arquivo CSV" in resultado
        assert "CSV" in resultado
        assert "https://example.com/dados.csv" in resultado
        assert "1.00 MB" in resultado

    def test_formatar_lista_recursos_vazia(self) -> None:
        resultado = formatar_lista_recursos([])
        assert "Nenhum" in resultado

    def test_formatar_analise_recurso_com_erro(self) -> None:
        resultado = formatar_analise_recurso({"erro": "Arquivo corrompido"})
        assert "Arquivo corrompido" in resultado

    def test_formatar_analise_recurso_csv(self) -> None:
        dados = {
            "formato": "CSV",
            "colunas": ["nome", "valor"],
            "total_linhas_lidas": 100,
            "linhas_exibidas": 20,
            "dados": [{"nome": "teste", "valor": "1"}],
        }
        resultado = formatar_analise_recurso(dados)

        assert "CSV" in resultado
        assert "nome, valor" in resultado
        assert "100" in resultado
