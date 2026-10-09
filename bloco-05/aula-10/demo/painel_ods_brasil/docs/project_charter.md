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

---

## Revisão para o TP3 (Etapa 5 · v7 — Aula 9)

> O enunciado do TP3 pede: *revise o Project Charter … reavalie o problema de negócio à luz das novas
> ferramentas … e ajuste suas metas, se necessário.* Esta é a revisão, feita no mesmo documento — o
> charter é vivo, e o histórico fica no Git.

**O que mudou no problema.** Nada no *porquê* (desigualdade regional, ODS 6 e 11). Mudou o *como o
usuário chega à resposta*: o painel reúne agora três fontes e seis perguntas, e numa página só a
gestora precisava rolar 360 linhas de interface até a resposta que queria.

**Metas acrescentadas (SMART):**
- **M4** — Cada pergunta do usuário acessível em **1 clique** a partir do menu (Etapa 5, Aula 9). ✅
- **M5** — Nenhuma página quebra quando aberta pelo **link direto** (Etapa 5, Aula 9). ✅
- **M6** — Uma **fonte dinâmica** (renderizada por JavaScript), coletada à parte (Etapa 5, Aula 10). ✅
  PRODES/INPE (TerraBrasilis) com Selenium: 342 linhas, 9 UFs, 1988–2025.
- **M7** — Uma **API própria** (FastAPI) que exponha os dados do painel, com ao menos uma rota de
  consulta (GET) e uma de envio (POST) (Etapa 6). 🔜

**KPI revisado:**

| KPI | Como medimos | Meta |
|-----|--------------|------|
| Usabilidade | nº de cliques para comparar 2 UFs | ≤ 3 → **mantida** (menu → Comparador → 2 marcações) |
| Navegabilidade | cliques do menu até qualquer resposta | **1** |

**Preparação para LLMs (pedido do TP3, item 5).** O texto das notícias coletadas
(`data/processed/noticias_texto.txt`, ~10 mil palavras) é o candidato natural para **resumo
automático** e **classificação de sentimento** nas Etapas 8–10. Por isso a coleta já guarda o texto
**completo**, e não só as manchetes.

### Revisão da Aula 10 (v8)

**ODS acrescentado:** **ODS 15 — Vida terrestre** (e, por consequência, **ODS 13 — Ação contra a
mudança global do clima**): a taxa anual de desmatamento da Amazônia Legal, por UF, passa a estar no
painel ao lado dos indicadores do IBGE.

**Risco novo e mitigação:**

| Risco | Mitigação |
|-------|-----------|
| A página dinâmica muda o JavaScript/estrutura e a coleta quebra | coleta **à parte**; guarda contra resultado incompleto (9 UFs); snapshot do HTML renderizado; o painel segue no ar com a última coleta boa |
| Coleta pesada (navegador) | roda **fora** do app e do Community Cloud; ~7 s por coleta, uma página só |
