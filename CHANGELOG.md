# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato segue o padrão [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [0.1.0] - 2026-02-28

### Adicionado

- Servidor MCP com Streamable HTTP transport
- **Portal SP** (`dadosabertos.sp.gov.br`):
  - `sp_buscar_conjuntos`: Pesquisa de conjuntos de dados por palavras-chave
  - `sp_detalhes_conjunto`: Metadados detalhados de conjuntos
  - `sp_listar_recursos`: Listagem de arquivos disponíveis em um conjunto
  - `sp_detalhes_recurso`: Metadados detalhados de recursos
  - `sp_baixar_e_analisar_recurso`: Download e análise de arquivos (CSV, JSON, XLSX, etc.)
  - `sp_listar_organizacoes`: Listagem de órgãos e entidades do Governo SP
  - `sp_listar_grupos`: Listagem de grupos temáticos
- **Portal Federal** (`dados.gov.br`):
  - `federal_buscar_conjuntos`: Pesquisa de conjuntos de dados por palavras-chave
  - `federal_detalhes_conjunto`: Metadados detalhados de conjuntos
  - `federal_listar_recursos`: Listagem de arquivos disponíveis em um conjunto
  - `federal_detalhes_recurso`: Metadados detalhados de recursos
  - `federal_baixar_e_analisar_recurso`: Download e análise de arquivos
  - `federal_listar_organizacoes`: Listagem de ministérios e autarquias
  - `federal_listar_temas`: Listagem de temas disponíveis
- Suporte a parsing de arquivos: CSV, CSV.GZ, JSON, JSONL, XLSX, XLS
- Detecção automática de encoding (UTF-8, Latin-1, CP1252)
- Detecção automática de delimitadores CSV (`,`, `;`, `\t`, `|`)
- Retry automático em falhas de rede (3 tentativas)
- Dockerfile e docker-compose.yml para deployment
- Testes unitários para helpers
- Testes de integração para os dois portais
- Documentação completa em português (pt-BR)
- Configuração de hooks de pre-commit com Ruff
