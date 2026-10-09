# Data Summary Report — Painel de Indicadores Sustentáveis do Brasil (v9 · Aula 11)

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
| 4 · PRODES/INPE (Selenium, v8) | 🌳 Desmatamento | legenda da página · ℹ️ Dados e método |


---

## Fonte 4 — Página DINÂMICA, coletada com Selenium (acrescentada na Aula 10 · subcomp. 3.2)

| Item | Valor |
|------|-------|
| Fonte | **PRODES/INPE — portal TerraBrasilis**, painel de taxas anuais de desmatamento |
| URL | `terrabrasilis.dpi.inpe.br/app/dashboard/deforestation/biomes/legal_amazon/rates` |
| Tipo | **Dinâmico**: o HTML entregue é uma casca (3.098 bytes; texto visível: "TerraBrasilis"); a tabela é montada pelo JavaScript no navegador |
| Permissão | `robots.txt` do portal **não proíbe** `/app/` (verificado com `urllib.robotparser`); sem `Crawl-delay` |
| Ritmo | **uma** página por coleta (o navegador faz as requisições que a própria página faz) |
| Licença | **Creative Commons Atribuição-CompartilhaIgual 4.0 (CC BY-SA 4.0)** — citar **e** manter a mesma licença no que derivar (inclusive o CSV que o painel deixa baixar) |
| Coleta | `src/coleta_dinamica.py`, **à parte**, com o ambiente de `requirements-coleta.txt` (Selenium + Chrome sem janela) |
| Espera | **explícita**, pela condição do dado: 9 UFs na tabela (esperar pelo elemento `<table>` devolvia 0 linhas) |
| Volume (23/09/2026) | **342 linhas · 9 UFs · 1988–2025 · ~7 s por coleta** (com a abertura do Chrome) |
| Saída | `data/processed/desmatamento_prodes.csv` · `desmatamento_meta.json` |
| Snapshot | `data/raw/prodes_renderizado.html` (o HTML **depois** do JavaScript) — **não versionado** |

### Por que Selenium — e a rota que NÃO usamos

A aba **Rede** (Network) das ferramentas do navegador mostra que a página baixa um JSON:
`…/files/rates2025.json`, com os valores por **código** de UF (`18278`), traduzidos por um **segundo**
arquivo (`config/loinames/prodes_legal_amazon.json`). É mais rápido que o Selenium — e é a rota que o
TP3 recomenda considerar ("mantendo a simplicidade quando possível").

**Decisão registrada:** coletamos pelo que a página **publica** (a tabela renderizada), porque o JSON é
**interno** ao app do INPE — não documentado, com o **ano no nome do arquivo** (`rates2025`) e
códigos que exigem uma segunda tradução. **Conferência cruzada** (23/09/2026): as duas rotas dão os
**mesmos 342 números** — zero diferenças. Se o seu projeto tiver um JSON assim **estável**, prefira-o.

### Dicionário de dados (`desmatamento_prodes.csv`)
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `uf` | texto (2) | Sigla da UF (mapeada do nome exibido na página) |
| `estado` | texto | Nome da UF como a página exibe |
| `ano` | inteiro | Ano do PRODES (período agosto–julho que termina neste ano) |
| `area_km2` | real | Taxa anual de desmatamento, em km² ("1.208,00 km²" → `1208.0`) |
| `fonte` | texto | Crédito exigido pela licença |

### Qualidade e observações
- Totais conferidos contra números públicos do PRODES: **2004 = 27.772 km²**, **2023 = 9.064 km²**,
  **2024 = 6.518 km²**; pico da série em **1995 (29.059 km²)**. O último ano é o dado mais recente
  publicado pelo painel na data da coleta.
- **Guarda:** a coleta não grava se vierem menos de 9 UFs, UF desconhecida ou zero linhas — preserva
  a última coleta boa.
- **Sem dado pessoal** (LGPD n/a).

---

## Saída para outros programas — a API do projeto (acrescentada na Aula 11 · subcomp. 3.3–3.4)

A v9 **não acrescenta fonte**: acrescenta uma **saída**. Até aqui o dado só chegava a **pessoas**, pelo
painel. Um programa que quisesse os nossos números teria de raspar o painel — e o painel, para o
`requests`, é uma **casca**: `status 200`, 10.951 bytes, texto visível *"You need to enable JavaScript
to run this app."*, nenhuma tabela (medido em 06/10/2026). Seria o **degrau 4** da escada da Aula 10.
A API é o **degrau 1** que o projeto oferece.

| Item | Valor |
|------|-------|
| Código | `api/main.py` — **FastAPI** |
| Como roda | **à parte**, na máquina de quem a usa: `uvicorn api.main:app --reload` (ambiente de `requirements-api.txt`) |
| De onde lê | dos **mesmos** arquivos de `data/processed/`, com as **mesmas** funções de `src/` que o painel usa — a API não coleta nada |
| Formato | JSON. As rotas de dados devolvem um **envelope**: `fonte`, `licenca`, `coletado_em`, `linhas`, `dados` |
| Documentação | gerada do próprio código: `/docs` (interativa) e `/redoc`; o esquema em `/openapi.json` |
| Licença | a de cada fonte **viaja com o dado** (campo `licenca`): CC BY-SA 4.0 (INPE) exige citar e compartilhar igual; CC BY 3.0 BR (Agência Brasil), citar |

### As rotas (todas GET, nesta versão)

| Rota | Parâmetros | Responde |
|------|------------|----------|
| `/` | — | o que a API serve e onde está a documentação |
| `/fontes` | — | procedência, data da coleta e licença de cada conjunto |
| `/desmatamento` | consulta: `desde` (≥ 1988), `ate` | a taxa anual de todas as UFs, no período |
| `/desmatamento/total` | consulta: `desde`, `ate` | a soma das nove UFs por ano — a taxa da Amazônia Legal |
| `/desmatamento/ranking/{ano}` | caminho: `ano` (inteiro ≥ 1988) | as UFs no ano, da que mais à que menos desmatou |
| `/desmatamento/{uf}` | caminho: `uf` (uma das 9 UFs); consulta: `desde`, `ate` | a série de uma UF |
| `/noticias` | consulta: `secao`, `limite` (1–50) | as notícias da última coleta |

**Exemplo:** `GET /desmatamento/PA?desde=2023` → `{"fonte": "INPE/PRODES — TerraBrasilis", "licenca":
"…(CC BY-SA 4.0)", "coletado_em": "01/10/2026 21:50", "linhas": 3, "dados": [{"uf": "PA", "ano": 2023,
"area_km2": 3299.0, …}, …]}`.

### Decisões registradas

- **O QUE vai no caminho; o COMO, na consulta.** A UF e o ano do ranking identificam **o recurso**
  (caminho); o período e o limite **recortam** a resposta (consulta).
- **Os tipos são a guarda.** `ano: int` e `uf` restrita às 9 UFs fazem o FastAPI recusar com **422** o
  que não serve (`abc`, `1950`, `ZZ`, `pa`) — **antes** de a função rodar. Sem o tipo, `ranking/2024`
  respondia **200 com lista vazia** (o ano chegava como texto). Ver o tropeço no comentário 🐛 de
  `api/main.py`.
- **Caminho fixo antes de caminho com parâmetro.** `/desmatamento/total` é declarada antes de
  `/desmatamento/{uf}` — na ordem inversa, "total" casava com `{uf}` e virava 422.
- **"Não encontrado" ainda responde 200** — um ranking de 2030 devolve `"linhas": 0`. É o
  comportamento do capítulo 2 do livro de referência; responder **404** com `HTTPException` (e
  declarar modelos de resposta) é a **Etapa 7**.
- **Sem dado pessoal** (LGPD n/a) — a API serve só dados públicos já coletados.
