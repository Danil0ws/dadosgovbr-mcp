"""
Testes de integração para as ferramentas do Portal Federal.

ATENÇÃO: Estes testes fazem requisições reais à API do Portal Federal.
Execute com: uv run pytest tests/test_federal.py -m integration -v

Nota: O Portal Federal (dados.gov.br) pode exigir autenticação para alguns endpoints.
Quando indisponível, as funções retornam mensagens de erro amigáveis — este
comportamento também é validado pelos testes.
"""

import pytest

from tools.federal import (
    baixar_e_analisar_recurso_federal,
    buscar_conjuntos_federal,
    detalhes_conjunto_federal,
    detalhes_recurso_federal,
    listar_organizacoes_federal,
    listar_recursos_federal,
    listar_temas_federal,
)


def _valida_resposta(resultado: str, contexto: str = "") -> None:
    """Valida que o resultado é uma string não vazia e útil."""
    assert isinstance(resultado, str), f"{contexto}: esperava str, obteve {type(resultado)}"
    assert len(resultado) > 10, f"{contexto}: resposta muito curta: {resultado!r}"


@pytest.mark.integration
class TestBuscarConjuntosFederal:
    """Testes de integração para busca de conjuntos no Portal Federal."""

    async def test_busca_simples(self) -> None:
        resultado = await buscar_conjuntos_federal("licitacoes")
        _valida_resposta(resultado, "busca_simples")

    async def test_busca_com_nota_sobre_autenticacao(self) -> None:
        """
        O Portal Federal pode retornar resultados ou uma nota sobre autenticação.
        Ambos os casos são válidos — a função nunca deve lançar exceção.
        """
        resultado = await buscar_conjuntos_federal("saude")
        _valida_resposta(resultado, "busca_saude")

    async def test_busca_sem_resultados(self) -> None:
        resultado = await buscar_conjuntos_federal("xyzxyzxyz12345aaabbbccc")
        _valida_resposta(resultado, "busca_sem_resultados")
        # Deve indicar "nenhum resultado" ou retornar uma mensagem de erro/auth
        assert any(
            termo in resultado.lower()
            for termo in ["nenhum", "0 resultado", "erro", "autenticação", "não encontrado"]
        )

    async def test_busca_com_paginacao(self) -> None:
        resultado_p1 = await buscar_conjuntos_federal("dados", pagina=1, tamanho_pagina=5)
        resultado_p2 = await buscar_conjuntos_federal("dados", pagina=2, tamanho_pagina=5)
        _valida_resposta(resultado_p1, "pagina_1")
        _valida_resposta(resultado_p2, "pagina_2")


@pytest.mark.integration
class TestDetalhesConjuntoFederal:
    """Testes de integração para detalhes de conjuntos no Portal Federal."""

    async def test_detalhes_conjunto_inexistente(self) -> None:
        """Um ID inválido deve retornar mensagem de erro, nunca lançar exceção."""
        resultado = await detalhes_conjunto_federal("conjunto-que-nao-existe-xyz-abc-123")
        _valida_resposta(resultado, "conjunto_inexistente")
        assert "erro" in resultado.lower() or "Erro" in resultado

    async def test_detalhes_retorna_string(self) -> None:
        """
        Qualquer chamada (com ou sem autenticação disponível) deve retornar str.
        """
        resultado = await detalhes_conjunto_federal("bolsa-familia")
        _valida_resposta(resultado, "detalhes_bolsa_familia")


@pytest.mark.integration
class TestListarRecursosFederal:
    """Testes de integração para listagem de recursos no Portal Federal."""

    async def test_listar_recursos_conjunto_inexistente(self) -> None:
        resultado = await listar_recursos_federal("conjunto-que-nao-existe-xyz")
        _valida_resposta(resultado, "recursos_inexistente")
        assert "erro" in resultado.lower() or "Erro" in resultado

    async def test_listar_recursos_retorna_string(self) -> None:
        resultado = await listar_recursos_federal("bolsa-familia")
        _valida_resposta(resultado, "recursos_bolsa_familia")


@pytest.mark.integration
class TestDetalhesRecursoFederal:
    """Testes de integração para detalhes de recurso no Portal Federal."""

    async def test_detalhes_recurso_id_invalido(self) -> None:
        """Um UUID inválido deve retornar mensagem de erro, nunca lançar exceção."""
        resultado = await detalhes_recurso_federal("00000000-0000-0000-0000-000000000000")
        _valida_resposta(resultado, "recurso_id_invalido")
        assert "erro" in resultado.lower() or "Erro" in resultado

    async def test_detalhes_recurso_retorna_string(self) -> None:
        resultado = await detalhes_recurso_federal("qualquer-id-para-testar")
        _valida_resposta(resultado, "recurso_retorna_string")


@pytest.mark.integration
class TestBaixarAnalisarRecursoFederal:
    """Testes de integração para download e análise de recurso no Portal Federal."""

    async def test_baixar_recurso_id_invalido(self) -> None:
        """Um ID inválido deve retornar mensagem de erro, nunca lançar exceção."""
        resultado = await baixar_e_analisar_recurso_federal("00000000-0000-0000-0000-000000000000")
        _valida_resposta(resultado, "baixar_id_invalido")
        assert "erro" in resultado.lower() or "Erro" in resultado

    async def test_baixar_retorna_string(self) -> None:
        resultado = await baixar_e_analisar_recurso_federal("qualquer-id-para-testar")
        _valida_resposta(resultado, "baixar_retorna_string")


@pytest.mark.integration
class TestListarOrganizacoesFederal:
    """Testes de integração para listagem de organizações no Portal Federal."""

    async def test_listar_organizacoes(self) -> None:
        resultado = await listar_organizacoes_federal()
        _valida_resposta(resultado, "listar_organizacoes")

    async def test_listar_organizacoes_paginado(self) -> None:
        resultado = await listar_organizacoes_federal(pagina=1, tamanho_pagina=10)
        _valida_resposta(resultado, "listar_organizacoes_paginado")


@pytest.mark.integration
class TestListarTemasFederal:
    """Testes de integração para listagem de temas no Portal Federal."""

    async def test_listar_temas(self) -> None:
        resultado = await listar_temas_federal()
        _valida_resposta(resultado, "listar_temas")
