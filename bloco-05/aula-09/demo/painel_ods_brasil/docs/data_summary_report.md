# Data Summary Report — Painel de Indicadores Sustentáveis do Brasil (v7 · Aula 9)

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

---

## Fonte 2 — WebScraping (acrescentada na Aula 7 · subcomp. 2.4)

| Item | Valor |
|------|-------|
| Fonte | **Agência Brasil (EBC)** — `agenciabrasil.ebc.com.br` |
| Seções | Meio ambiente · Direitos humanos · Economia |
| Tipo | **Não estruturado** (HTML feito para leitores humanos) — não há API |
| Permissão | `robots.txt` **permite** as seções (verificado com `urllib.robotparser`) |
| Ritmo | `Crawl-delay: 10 s` — **respeitado** pelo coletor |
| Licença | **Creative Commons Atribuição 3.0 Brasil** — reutilizável **com citação** |
| Coleta | `src/coleta_web.py`, executado **à parte** (não pelo app) |
| Volume (02/09/2026) | **15 notícias · 3 seções · 10.182 palavras · 186 s** |
| Saída | `data/processed/noticias.csv` · `noticias_texto.txt` · `coleta_meta.json` |
| Snapshot | `data/raw/*.html` — **não versionado** (conteúdo de terceiros, regenerável) |

### Por que esta fonte, e não outra
Duas candidatas foram descartadas **antes** de qualquer código, e o motivo faz parte do registro:

| Candidata | Resultado | Decisão |
|-----------|-----------|---------|
| Agência IBGE Notícias | **HTTP 403** — o servidor recusou o cliente | descartada |
| ONU News (pt), seção ODS | `robots.txt`: **`Disallow: */news/`** — a URL desejada casa com o padrão | descartada |
| **Agência Brasil (EBC)** | 200 · permitido · licença aberta | **escolhida** |

### Dicionário de dados (`noticias.csv`)
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `secao` | texto | Seção do site de onde a manchete veio |
| `titulo` | texto | Manchete, já limpa (` `, espaços repetidos) |
| `publicado_em` | texto `dd/mm/aaaa hh:mm` | Data da matéria, extraída da página da notícia |
| `palavras` | inteiro | Tamanho do texto completo (insumo da contagem de palavras) |
| `url` | texto | Link absoluto da matéria |
| `fonte` | texto | Crédito exigido pela licença |

### Pipeline (dois níveis = *web crawling*)
`robots.txt` (posso?) → seção (manchetes + links) → **snapshot** → matéria (data + texto) →
limpeza → CSV/TXT. Guarda: **nunca gravar por cima quando a extração devolve zero linhas**.

### Qualidade e observações
- Conteúdo jornalístico, público e sob licença aberta; **sem dado pessoal** (LGPD n/a).
- A estrutura da página é **escolha do dono do site** e pode mudar sem aviso — por isso a coleta
  roda **separada** do app: se o seletor quebrar, o painel continua no ar com a última coleta.
- `?page=1` na Agência Brasil devolve **200 com zero manchetes**: paginação que parece existir e
  não existe. Verificado, e não suposto.

## Fonte 3 — Arquivo enviado pelo usuário (acrescentada na Aula 8 · subcomp. 2.3)

| Item | Valor |
|------|-------|
| Origem | CSV enviado pelo próprio usuário via `st.file_uploader` |
| Tipo | Estruturado (CSV), **entrada NÃO CONFIÁVEL** |
| Colunas obrigatórias | `secao`, `titulo`, `url` |
| Validação | `src/noticias.py :: ler_csv_enviado()` — devolve `(linhas, erro)`, **nunca levanta exceção** |
| Codificações aceitas | `utf-8-sig` → `utf-8` → `latin-1` (nessa ordem: `latin-1` nunca falha) |
| Onde vive | `st.session_state["noticias_enviadas"]` — **privado da sessão**, nunca no cache |
| Procedência | cada linha recebe `origem = "enviado"`; a tabela mostra *coletada* × *enviada* |

> **Nunca cacheado.** `@st.cache_data` é compartilhado entre visitantes: cachear o arquivo de um
> usuário faria o próximo ver o conteúdo do anterior. Não é performance — é vazamento.

## Derivado — contagem de palavras (Aula 8)
`src/analise_texto.py` lê `data/processed/noticias_texto.txt` e produz a frequência de termos
(`collections.Counter`) e as estatísticas básicas pedidas pelo TP2. Medido: **10.439 palavras ·
5.172 fora as palavras vazias · 2.372 de vocabulário distinto**. A lista de **palavras vazias** é
**decisão editorial**, mantida visível no código e revisada olhando o resultado.

---

## Revisão para o TP3 — onde cada fonte aparece (v7 · Aula 9)

A v7 **não acrescentou fonte**: reorganizou o painel em páginas. O registro relevante para o Data
Summary Report é **qual página exibe qual dado** — é o que permite a quem lê o relatório encontrar o
dado no produto, e a quem usa o produto encontrar a origem no relatório.

| Fonte | Página(s) que a exibem | Onde a licença/procedência aparece |
|-------|------------------------|------------------------------------|
| 1–3 · IBGE (API + cache) | 📊 Indicadores · ⭐ Comparador · 🏠 Início (métricas) | legenda "Fonte:" em cada página · ℹ️ Dados e método |
| 2 · Agência Brasil (WebScraping) | 📰 Notícias · 🔤 Palavras | rodapé de Notícias · ℹ️ Dados e método |
| 3 · CSV do usuário | 📰 Notícias (coluna *Origem*) | ℹ️ Dados e método (contagem da sessão) |

> **Próxima revisão (Aula 10):** uma fonte **dinâmica**, coletada com Selenium, entra aqui como
> Fonte 4 — com a mesma ficha (permissão, licença, ritmo, volume, dicionário de dados).
