# Project Charter — Painel de Indicadores Sustentáveis do Brasil

> Artefato da fase **Entendimento do Negócio** do ciclo de vida **TDSP**.
> Documento vivo: revisado ao final de cada etapa do projeto.

## 1. Contexto e problema de negócio
Indicadores socioambientais brasileiros (saneamento, meio ambiente, população)
estão dispersos em portais distintos, dificultando a **comparação entre UFs** e a
**priorização de ações** por gestores públicos e ONGs. Falta uma visão unificada e
interativa alinhada aos ODS da Agenda 2030.

## 2. Objetivos e metas
- **Objetivo geral:** disponibilizar um painel interativo que compare indicadores
  de sustentabilidade por Unidade da Federação.
- **Metas (SMART):**
  - M1 — Reunir ≥ 1 indicador oficial do IBGE para as 27 UFs até a Aula 2.
  - M2 — Permitir filtro por região e por UF na interface.
  - M3 — Publicar a primeira versão navegável do painel até o fim do 1º ciclo.

## 3. Indicadores de sucesso (KPIs)
| KPI | Como medimos | Meta |
|-----|--------------|------|
| Cobertura de dados | nº de UFs com dado carregado | 27/27 |
| Atualidade | ano do dado mais recente exibido | ≤ 1 ano |
| Usabilidade | nº de cliques para comparar 2 UFs | ≤ 3 |

## 4. ODS atendido e justificativa
- **ODS 6 — Água potável e saneamento** e **ODS 11 — Cidades e comunidades sustentáveis.**
- Justificativa: ao tornar visíveis as desigualdades regionais de saneamento e
  infraestrutura urbana, o painel apoia decisões que reduzem essas lacunas.

## 5. Público-alvo (stakeholders)
- **Primário:** gestores públicos municipais/estaduais.
- **Secundário:** ONGs de impacto socioambiental; pesquisadores; imprensa de dados.

## 6. Escopo
- **Dentro:** coleta via API pública do IBGE, tratamento, visualização por UF/região.
- **Fora (por ora):** dados municipais detalhados; previsões; integração com LLMs
  (entra nas etapas finais do PB).

## 7. Fontes de dados previstas
Ver `data_summary_report.md`.

## 8. Riscos e mitigação
| Risco | Mitigação |
|-------|-----------|
| Indisponibilidade da API em sala/produção | *fallback* para amostra em cache (`data/sample/`) |
| Mudança no formato da resposta da API | função de acesso isolada em `src/` + testes |
