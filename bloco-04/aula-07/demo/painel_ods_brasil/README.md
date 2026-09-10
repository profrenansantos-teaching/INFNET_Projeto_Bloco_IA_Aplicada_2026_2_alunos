# Painel de Indicadores Sustentáveis do Brasil — v5

Demo do **Projeto de Bloco: Inteligência Artificial Aplicada** (INFNET) · **Aula 7 · PB Etapa 4**.

Painel ESG/ODS em **Python puro** (sem pandas). Esta versão (**v5**) acrescenta à v4 uma **segunda
fonte de dados** — notícias raspadas da **Agência Brasil (EBC)**, que **não tem API**. A camada de
interação não mudou; o que mudou foi de onde os dados vêm.

## Rodar localmente

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows  ·  source .venv/bin/activate no macOS/Linux
pip install -r requirements.txt

python -m src.coleta_web          # 1) COLETA (roda à parte, ~3 min) -> data/processed/
streamlit run app.py              # 2) USO
```

> **A ordem importa, e é o assunto da aula.** O `app.py` **não raspa**: ele lê os arquivos que a
> coleta gravou. Sem o passo 1, o painel abre e avisa que não há notícias — não quebra.

Camadas rodáveis sem interface:

```bash
python -m src.data_access      # coleta as 27 UFs via API (ou usa o cache)
python -m src.transformacoes   # filtra, ordena, resume, compara e exporta CSV
python -m src.noticias         # lê o CSV das notícias e resume a coleta
```

## O que mudou da v4 para a v5

| # | Mudança | Ferramenta | Por quê |
|---|---------|-----------|---------|
| 1 | **Segunda fonte**: manchetes da Agência Brasil | `requests` + `BeautifulSoup` | a gestora pediu o que **não tem API** |
| 2 | **`src/coleta_web.py`** — o raspador, executado **à parte** | script, não módulo do app | o `robots.txt` da EBC pede `Crawl-delay: 10` |
| 3 | Verificação de **permissão** antes de baixar | `urllib.robotparser` (biblioteca padrão) | `robots.txt` + `Crawl-delay` + licença, nessa ordem |
| 4 | **Snapshot** do HTML baixado | `data/raw/*.html` | reprocessar sem nova requisição — e prova do que a página dizia |
| 5 | **Dois níveis** (seção → matéria) | *web crawling* | a data exata e o texto só existem na matéria |
| 6 | **`src/noticias.py`** — leitura do CSV | módulo `csv` | o app não sabe o que é HTML |
| 7 | Crédito da licença no rodapé | — | CC **Atribuição** 3.0: reutilizar exige citar |

## Estrutura — a coleta é uma etapa, não um recurso do app

```
painel_ods_brasil/
├── app.py                          INTERFACE  — nunca toca na rede para buscar notícia
├── src/
│   ├── coleta_web.py               COLETA     — raspa (roda ANTES, à parte)   ← novo
│   ├── data_access.py              DADOS      — API do IBGE + fallback
│   ├── noticias.py                 DADOS      — lê o CSV da coleta            ← novo
│   └── transformacoes.py           LÓGICA     — filtrar, ordenar, exportar
├── data/
│   ├── raw/*.html                  snapshots (NÃO versionados)                ← novo
│   ├── processed/noticias.csv      o que o app lê (VERSIONADO)                ← novo
│   ├── processed/noticias_texto.txt   matéria-prima da Aula 8                 ← novo
│   ├── processed/coleta_meta.json  quando, de onde, sob qual licença          ← novo
│   └── sample/ufs_cache.json       cache de emergência da API
├── requirements.txt · .gitignore · DEPLOY.md
└── .streamlit/config.toml · secrets.toml.example
```

**Por que `data/raw/` não é versionado:** é conteúdo de **terceiros**, pesa megabytes e é
**regenerável**. O repositório do Community Cloud é público. Já `data/processed/` **é** versionado —
é dele que o app publicado vive.

## A fonte, e por que esta

**Agência Brasil (EBC)** — seções *Meio ambiente*, *Direitos humanos* e *Economia*.

| Critério | Situação (verificada em 02/09/2026) |
|----------|--------------------------------------|
| Acesso | HTTP 200, HTML renderizado no servidor |
| `robots.txt` | permite as seções; proíbe internos do Drupal |
| `Crawl-delay` | **10 segundos** — declarado, e respeitado pelo coletor |
| Licença | **Creative Commons Atribuição 3.0 Brasil** — reutilizável **com citação** |

**Alvos descartados** (viram estudo de caso na aula): **Agência IBGE Notícias** devolveu **403**;
**ONU News** proíbe `*/news/` no `robots.txt`, exatamente o padrão da URL desejada.

## Modos do coletor

```bash
python -m src.coleta_web             # 3 seções, 15 matérias  (~186 s, respeitando o Crawl-delay)
python -m src.coleta_web --rapido    # 1 seção, 2 matérias    (~30 s — para demonstrar em aula)
python -m src.coleta_web --do-cache  # reprocessa o snapshot, SEM tocar na rede
```

O `--do-cache` é a rede de segurança da aula: se a internet cair, ou se o site mudar no meio da
demonstração, a coleta é refeita a partir do HTML já gravado.

## Publicar

Mesmo repositório da Aula 5 — roteiro completo em [`DEPLOY.md`](DEPLOY.md):

```bash
git add .
git commit -m "v5: coleta web da Agencia Brasil + secao de noticias"
git push
```

O rodapé mostra `v5 — Aula 7 (extração de conteúdo web)`.

## Verificação

Confirmado por execução, não por leitura (02/09/2026):

- coleta real: **15 notícias · 3 seções · 10.182 palavras · 186 s**, respeitando o `Crawl-delay`;
- `can_fetch` → **True** para `/meio-ambiente` e `/economia`, **False** para `/admin/config` e
  `/cron.php`; `crawl_delay` → **10**;
- página de seção: **170 links**, 27 apontando para `/noticia/`, **5 manchetes distintas**
  (a mesma matéria aparece duas vezes: destaque + lista);
- `AppTest` (Streamlit 1.61): render sem exceção, **duas fontes na tela**, e desmarcar todas as
  seções de notícias produz um **aviso** — não um erro.

## Configuração

Igual à v3: `PAINEL_ODS_VERIFICAR_SSL` (ambiente) ou `verificar_ssl` (`secrets.toml`) — padrão
**seguro**. Na rede da escola, com proxy TLS, é preciso desligar explicitamente. Ver `DEPLOY.md`.
