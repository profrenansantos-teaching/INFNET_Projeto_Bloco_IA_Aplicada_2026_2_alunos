# Data Summary Report — Painel de Indicadores Sustentáveis do Brasil

> Artefato das fases **Entendimento do Negócio → Aquisição e Entendimento dos Dados** (TDSP).
> Primeiro esboço: relaciona as fontes de dados, o tipo e o objetivo de uso.

## Fontes de dados
| # | Fonte | Tipo de dado | Acesso | Objetivo de uso | Status |
|---|-------|--------------|--------|-----------------|--------|
| 1 | IBGE — População residente estimada (tabela 6579) | Estruturado (JSON via API) | `servicodados.ibge.gov.br/api/v3/agregados` | Denominador e primeiro indicador do painel | Amostra manual (Aula 1) → API (Aula 2) |
| 2 | IBGE — Localidades (estados) | Estruturado (JSON via API) | `servicodados.ibge.gov.br/api/v1/localidades/estados` | Nomes, siglas e regiões das UFs | Validado |
| 3 | IBGE — Saneamento (Censo, ex.: esgotamento sanitário) | Estruturado (JSON via API) | `servicodados.ibge.gov.br/api/v3/agregados` | Indicador ESG (ODS 6) — etapa seguinte | Planejado |

## Dicionário de dados (amostra atual — `data/sample/populacao_amostra.csv`)
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `uf` | texto (2) | Sigla da Unidade da Federação |
| `estado` | texto | Nome do estado |
| `regiao` | texto | Grande região (Norte, Nordeste, …) |
| `populacao_2025` | inteiro | População residente estimada em 2025 (pessoas) |

## Qualidade e observações
- Dados oficiais e de domínio público; sem informação pessoal (LGPD n/a).
- Respostas da API vêm **compactadas (gzip)** e em **JSON** — tratadas no código da Aula 2.
- Período mais recente disponível na tabela 6579: **2025**.
