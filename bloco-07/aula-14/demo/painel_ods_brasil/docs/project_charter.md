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

### Revisão da Aula 11 (v9) — a API do projeto

> O TP3 pede: *reavalie o problema de negócio à luz das novas ferramentas (como FastAPI e Selenium)*.

**O que mudou no problema.** Um **público novo**: além de pessoas, **programas**. A prefeitura parceira
quer os números do painel no sistema dela — e raspar o nosso painel seria subir ao degrau 4 da escada
(ele é uma página dinâmica). O projeto passa a oferecer o **degrau 1**: uma API documentada.

| Seção | Revisão |
|-------|---------|
| **5. Público-alvo** | + **sistemas de terceiros** (prefeituras, ONGs, pesquisadores que automatizam análises) |
| **6. Escopo — dentro** | + **API própria (FastAPI)** que serve, em JSON, os dados já coletados — rodando **localmente** nesta etapa |
| **6. Escopo — fora** | publicar a API num servidor; autenticação; escrita de dados por terceiros (a Aula 12 trata o envio) |
| **Meta nova (M6)** | toda pergunta que o painel responde tem **um endereço** na API, documentado em `/docs` |
| **KPI novo** | rotas documentadas / rotas existentes = **100%** (o `/docs` é gerado do código: a meta é descrever cada rota) |

**Riscos novos e mitigação:**

| Risco | Mitigação |
|-------|-----------|
| A licença se perde quando o dado sai pela API | toda resposta de dados traz `fonte`, `licenca` e `coletado_em` |
| A API e o painel divergem (cada um lendo do seu jeito) | os dois usam as **mesmas** funções de `src/` sobre os **mesmos** arquivos |
| Pedido malformado devolve resposta errada sem erro | **tipos** nos parâmetros: o FastAPI recusa com 422 o que não converte |

### Revisão da Aula 12 (v10) — a API recebe

**O que mudou no problema.** O projeto passa a **receber** informação, não só a publicar: equipes de
campo e moradores relatam o que veem (queimadas, cheias, descarte de lixo). O painel deixa de ser só
vitrine de dados oficiais — e ganha um canal de **dado local**, que nenhuma das fontes oficiais tem.

| Seção | Revisão |
|-------|---------|
| **5. Público-alvo** | + **equipes de campo e moradores** (quem envia relatos) |
| **6. Escopo — dentro** | + `POST /relatos` (validado) e a página **Relatos de campo**, que o usa |
| **6. Escopo — fora** | moderação dos relatos; autenticação de quem envia; publicar a API |
| **Meta nova (M7)** | um relato enviado pela página aparece na lista **sem recarregar** e **sem** dado pessoal gravado |
| **KPI novo** | % de envios recusados **com mensagem compreensível** (o 422 traduzido na página) = 100% |

**Riscos novos e mitigação:**

| Risco | Mitigação |
|-------|-----------|
| Dado pessoal no relato | modelo recusa campos extras; aviso na entrada; `data/relatos/` fora do Git |
| Relato falso ou ofensivo | aviso "não verificado pelo projeto"; moderação fica fora do escopo (registrado) |
| Dois envios ao mesmo tempo corrompem a numeração | trava em `src/relatos.py` (medido: sem ela, 40 envios → 9 números) |
| A API fora do ar | a página avisa, desliga o envio e mostra exemplos — o plano B da Aula 2 |

### Revisão da Aula 13 (v11) — a API declara o que responde

**O que mudou no problema.** O técnico da prefeitura, que consome a API desde a v9, integrou o sistema dele
**adivinhando** o formato das respostas (o `/docs` dizia `"string"` para todas) — e o sistema quebrou no
`/fontes`, que devolvia três formatos numa lista. E a gestora quer saber, **antes** do LLM chegar, em que
formato a análise de texto vai responder, para a prefeitura se preparar. A pergunta deixa de ser "que dados a
API tem" e passa a ser **"o que exatamente a API promete devolver"**.

| Seção | Revisão |
|-------|---------|
| **6. Escopo — dentro** | + **modelo de resposta** em toda rota; + `POST /processar_texto` (a rota do TP4) com um motor **provisório** de regras; + página **Analisador** |
| **6. Escopo — fora** | o modelo LLM (Etapa 8); erros HTTP específicos — 404, 503 (Aula 14) |
| **Meta nova (M8)** | toda rota com formato de resposta **declarado** no `/docs` (nenhum `"string"`) |
| **KPI novo** | rotas com `response_model` / rotas existentes = **100%** (v10: 0 de 9) |

**Riscos novos e mitigação:**

| Risco | Mitigação |
|-------|-----------|
| A API publica o que a função calcula a mais (detalhes internos, colunas repetidas) | o modelo de resposta **filtra**: só sai o que está no contrato |
| Prometer um tipo que o dado não cumpre (ex.: `datetime` para `"02/09/2026 08:16"`) | declarar o que o dado **é** (texto `dd/mm/aaaa hh:mm`); o 500 da validação aparece no teste, não no cliente |
| Trocar o motor de análise quebra quem já usa a rota | o **contrato vem antes do motor**: `ResultadoAnalise` não muda quando o LLM entrar |
| Mudar o status (200 → 201) quebra cliente que confere `== 200` | documentar no `/docs`; recomendar conferir a família (`2xx`), não o número |

### Revisão da Aula 14 (v12) — quando dá errado, a API diz o quê

**O que mudou no problema.** O relatório mensal da prefeitura, montado com a nossa API, registrou **"nenhum
desmatamento em 2026"** — o PRODES ainda não publicou a taxa de 2026, e a API respondia `200` com zero linhas.
Um erro que parecia sucesso virou uma informação falsa num documento oficial. E, numa semana, a análise de
texto parou porque o arquivo de regras não veio para a máquina de um colega — e com ela parou a API inteira.
O risco deixa de ser "a API não ter o dado" e passa a ser **a API não dizer que não tem**.

| Seção | Revisão |
|-------|---------|
| **6. Escopo — dentro** | + respostas de erro com o **status certo** e uma frase (404, 409, 503); + 500 em JSON com código; + `GET /relatos/{id}`; + erros declarados no `/docs` |
| **6. Escopo — fora** | autenticação (401/403); limite de pedidos (429); publicar a API |
| **Meta nova (M9)** | nenhuma falha prevista responde 200; nenhum 500 sai em texto puro nem com traceback |
| **KPI novo** | erros previstos documentados no `/docs` / erros previstos = **100%** (v11: 0 — o 404 nem existia) |

**Riscos novos e mitigação:**

| Risco | Mitigação |
|-------|-----------|
| Um 200 vazio lido como "zero" (ranking de um ano sem dado) | **404** com a faixa de anos que existe; o critério identificar (404) × recortar (200 `[]`) |
| Uma peça quebrada derrubar a API inteira (o motor de análise) | carregar com `try`; a API sobe e só a rota afetada responde **503** — falhe em pedaços |
| O mesmo relato gravado várias vezes (o sinal caiu, o usuário reenviou) | **409** com o número do relato já gravado |
| Traceback ou caminho de arquivo exposto num erro | a rede de segurança: ao cliente, a frase e um código; ao log, o traceback |
| O painel esconder ou distorcer a resposta da API | o painel lê **pelo status** e mostra a frase da API; avisos (409, 503) × erros (422, 500) |
