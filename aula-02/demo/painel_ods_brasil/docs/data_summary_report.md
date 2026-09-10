# Data Summary Report — Painel de Indicadores Sustentáveis do Brasil (Aula 2)

> Artefato TDSP (Aquisição e Entendimento dos Dados). Atualizado na Aula 2: a amostra manual deu
> lugar à **coleta automática via API do IBGE** (27 UFs).

## Fontes de dados
| # | Fonte | Tipo | Endpoint | Objetivo de uso | Status |
|---|-------|------|----------|-----------------|--------|
| 1 | IBGE — Localidades (estados) | Estruturado (JSON via API) | `/api/v1/localidades/estados` | Sigla, nome e região das 27 UFs | ✅ coletado ao vivo |
| 2 | IBGE — População estimada (tab. 6579, var. 9324) | Estruturado (JSON via API) | `/api/v3/agregados/6579/periodos/-1/variaveis/9324?localidades=N3[all]` | Indicador-base por UF | ✅ coletado ao vivo (2025) |
| 3 | Cache local (`data/sample/ufs_cache.json`) | JSON | arquivo | *Fallback* se a API estiver indisponível | ✅ |
| 4 | IBGE — Saneamento (Censo) | Estruturado (JSON via API) | a definir | Indicador ESG (ODS 6) | 🔜 próxima etapa |

## Pipeline de coleta (Python puro)
`src/data_access.py`: `requests` faz as 2 chamadas → o **JSON (semi-estruturado)** é transformado numa
**lista de dicionários (tabela)**; ids convertidos de texto para inteiro; população para inteiro.
Em caso de falha de rede, cai para o **cache**. A camada de dados é **isolada** da interface (`app.py`).

## Dicionário de dados (saída)
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `uf` | texto (2) | Sigla da UF |
| `estado` | texto | Nome do estado |
| `regiao` | texto | Grande região |
| `populacao_2025` | inteiro | População residente estimada (2025) |

## Qualidade e observações
- Dados oficiais e públicos; sem dado pessoal (LGPD n/a).
- A resposta da API vem **comprimida (gzip)** — o `requests` descomprime automaticamente.
- Período mais recente da tabela 6579: **2025**.
