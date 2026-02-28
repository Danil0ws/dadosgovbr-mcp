"""
Testes de integração para as ferramentas do Portal SP.

ATENÇÃO: Estes testes fazem requisições reais à API do Portal SP.
Execute com: uv run pytest tests/test_sp.py -m integration -v

Para rodar apenas testes unitários (sem rede):
uv run pytest tests/test_sp.py -m "not integration" -v
"""

import pytest

from tools.sp import (
    baixar_e_analisar_recurso_sp,
    buscar_conjuntos_sp,
    detalhes_conjunto_sp,
    detalhes_recurso_sp,
    listar_grupos_sp,
    listar_organizacoes_sp,
    listar_recursos_sp,
)

# ID de recurso real do conjunto "multas-pagas" (CSV público, pequeno)
ID_RECURSO_REAL = "3b4ea0c5-832c-49ae-9209-76a0cccb6918"


@pytest.mark.integration
class TestBuscarConjuntosSP:
    """Testes de integração para busca de conjuntos no Portal SP."""

    async def test_busca_simples(self) -> None:
        resultado = await buscar_conjuntos_sp("transporte")
        assert isinstance(resultado, str)
        assert len(resultado) > 0
        # Não deve retornar erro
        assert "Erro" not in resultado[:50]

    async def test_busca_sem_resultados(self) -> None:
        resultado = await buscar_conjuntos_sp("xyzxyzxyz12345aaabbbccc")
        assert isinstance(resultado, str)
        # Deve indicar que não encontrou ou retornar lista vazia
        assert "0" in resultado or "Nenhum" in resultado

    async def test_busca_com_paginacao(self) -> None:
        resultado_p1 = await buscar_conjuntos_sp("dados", pagina=1, tamanho_pagina=5)
        resultado_p2 = await buscar_conjuntos_sp("dados", pagina=2, tamanho_pagina=5)
        assert isinstance(resultado_p1, str)
        assert isinstance(resultado_p2, str)
        # As páginas devem ser diferentes
        assert resultado_p1 != resultado_p2


@pytest.mark.integration
class TestDetalhesConjuntoSP:
    """Testes de integração para detalhes de conjuntos no Portal SP."""

    async def test_detalhes_por_slug(self) -> None:
        resultado = await detalhes_conjunto_sp("multas-pagas")
        assert isinstance(resultado, str)
        # Deve retornar informações do conjunto ou erro específico
        assert len(resultado) > 0

    async def test_conjunto_inexistente(self) -> None:
        resultado = await detalhes_conjunto_sp("conjunto-que-nao-existe-xyz")
        assert isinstance(resultado, str)
        assert "Erro" in resultado or "erro" in resultado.lower()


@pytest.mark.integration
class TestListarRecursosSP:
    """Testes de integração para listagem de recursos no Portal SP."""

    async def test_listar_recursos(self) -> None:
        resultado = await listar_recursos_sp("multas-pagas")
        assert isinstance(resultado, str)
        assert len(resultado) > 0


@pytest.mark.integration
class TestListarOrganizacoesSP:
    """Testes de integração para listagem de organizações no Portal SP."""

    async def test_listar_organizacoes(self) -> None:
        resultado = await listar_organizacoes_sp()
        assert isinstance(resultado, str)
        assert "detran" in resultado.lower() or "secretaria" in resultado.lower()


@pytest.mark.integration
class TestListarGruposSP:
    """Testes de integração para listagem de grupos no Portal SP."""

    async def test_listar_grupos(self) -> None:
        resultado = await listar_grupos_sp()
        assert isinstance(resultado, str)
        assert len(resultado) > 0
        # Deve conter alguns dos grupos conhecidos
        assert any(
            tema in resultado.lower() for tema in ["saude", "educacao", "transporte", "seguranca"]
        )


@pytest.mark.integration
class TestDetalhesRecursoSP:
    """Testes de integração para detalhes de recurso no Portal SP."""

    async def test_detalhes_recurso_existente(self) -> None:
        resultado = await detalhes_recurso_sp(ID_RECURSO_REAL)
        assert isinstance(resultado, str)
        assert len(resultado) > 0
        assert "Erro" not in resultado[:50]

    async def test_detalhes_recurso_inexistente(self) -> None:
        resultado = await detalhes_recurso_sp("00000000-0000-0000-0000-000000000000")
        assert isinstance(resultado, str)
        assert "erro" in resultado.lower() or "Erro" in resultado


@pytest.mark.integration
class TestBaixarAnalisarRecursoSP:
    """Testes de integração para download e análise de recurso no Portal SP."""

    async def test_baixar_csv(self) -> None:
        resultado = await baixar_e_analisar_recurso_sp(
            ID_RECURSO_REAL, max_linhas=5, max_tamanho_mb=10
        )
        assert isinstance(resultado, str)
        assert len(resultado) > 0
        # Deve conter o cabeçalho com URL ou o nome do recurso
        assert "Recurso:" in resultado or "URL:" in resultado

    async def test_baixar_recurso_inexistente(self) -> None:
        resultado = await baixar_e_analisar_recurso_sp("00000000-0000-0000-0000-000000000000")
        assert isinstance(resultado, str)
        assert "erro" in resultado.lower() or "Erro" in resultado
