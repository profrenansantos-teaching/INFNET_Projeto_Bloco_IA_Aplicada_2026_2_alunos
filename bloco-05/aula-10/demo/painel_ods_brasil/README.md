# Painel de Indicadores Sustentáveis do Brasil — v8

Demo do **Projeto de Bloco: Inteligência Artificial Aplicada** (INFNET) · **Aula 10 · PB Etapa 5**.

Painel ESG/ODS em **Python puro** (sem pandas). Esta versão (**v8**) acrescenta a **quarta fonte**:
a taxa anual de **desmatamento por UF** do **PRODES/INPE**, tirada de uma página que **só mostra a
tabela depois que o JavaScript roda** — coletada com **Selenium**, **à parte**. No app, isso custou
uma linha no menu e uma leitura cacheada: é o que a divisão em páginas da v7 comprou.

## Dois ambientes, dois arquivos de requisitos

| Para… | Instale | O que vem |
|-------|---------|-----------|
| **usar** o app (e o que o Community Cloud instala) | `pip install -r requirements.txt` | Streamlit, requests, urllib3, beautifulsoup4 |
| **coletar** a fonte dinâmica (só na sua máquina) | `pip install -r requirements-coleta.txt` | tudo acima **+ selenium** |

> O app **não importa** o Selenium: no `requirements.txt` ele seria peso morto no *build* do Community
> Cloud. *O que se importa, se declara* (Aula 5): **no arquivo do ambiente que importa**.
>
> **E se eu quisesse o Selenium no app publicado?** Dá: o Community Cloud não traz navegador, mas
> instala o Chromium via `packages.txt`. Não é o que a v8 faz — ver `DEPLOY.md` §10.1 e o exemplo
> testado em `../../aula-10-step-by-step/passo06_selenium_no_app/`.

## Rodar localmente

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1                 # Windows  ·  source .venv/bin/activate no macOS/Linux
pip install -r requirements-coleta.txt     # a coleta precisa do Selenium (e do Google Chrome instalado)

python -m src.coleta_web                   # 1a) COLETA estática (Aula 7)  -> data/processed/noticias*
python -m src.coleta_dinamica              # 1b) COLETA dinâmica (Aula 10) -> data/processed/desmatamento*
streamlit run app.py                       # 2)  USO
```

Sem rede e sem navegador, dá para **reprocessar** a última coleta dinâmica a partir do snapshot:

```bash
python -m src.coleta_dinamica --do-snapshot
python -m src.desmatamento                 # a lógica, sem Streamlit: totais, ranking, pico da série
```

## O que mudou da v7 para a v8

| # | Mudança | Ferramenta | Por quê |
|---|---------|-----------|---------|
| 1 | Coletor de **página dinâmica** | `src/coleta_dinamica.py` — Selenium + Chrome sem janela | o `requests` recebe uma casca: 3.098 bytes, texto visível "TerraBrasilis" |
| 2 | **Espera explícita pela condição do dado** (9 UFs) | `WebDriverWait` | esperar pela `<table>` devolvia **0 linhas** (🐛 tropeço da v8) |
| 3 | Extração com **BeautifulSoup** sobre o `page_source` | `extrair_tabela(html)` | o Selenium só roda o JS; extrair é a Aula 7 — testável sem navegador |
| 4 | **Snapshot** do HTML renderizado + **guarda** (9 UFs) | `data/raw/` · `conferir()` | reprocessar sem rede; nunca gravar por cima com resultado incompleto |
| 5 | Página **🌳 Desmatamento (PRODES)** | `paginas/desmatamento.py` | UFs + período (preservados), evolução, ranking do ano, CSV |
| 6 | Lógica pura da fonte nova | `src/desmatamento.py` | totais, ranking, variação — sem Streamlit |
| 7 | `requirements-coleta.txt` | `-r requirements.txt` + `selenium` | o ambiente da coleta ≠ o ambiente do app |

## Estrutura

```
painel_ods_brasil/
├── app.py                    ROTEADOR   — + a página Desmatamento no menu                  ← 1 linha
├── comum.py                  COMUM      — + obter_desmatamento() (cacheada)                 ← ampliado
├── paginas/
│   ├── desmatamento.py       🌳 evolução por UF, ranking do ano, download                     ← novo
│   └── …                     (as seis da v7; Início e Dados e método citam a fonte nova)
├── src/
│   ├── coleta_dinamica.py    COLETA     — Selenium, À PARTE (requirements-coleta.txt)         ← novo
│   ├── desmatamento.py       DADOS + LÓGICA — lê o CSV; sem Streamlit, sem Selenium           ← novo
│   └── …                     (coleta_web, data_access, noticias, analise_texto, transformacoes)
├── data/processed/           desmatamento_prodes.csv + desmatamento_meta.json (VERSIONADOS)
├── data/raw/                 prodes_renderizado.html (NÃO versionado)
├── requirements.txt          o app (e o Community Cloud)
└── requirements-coleta.txt   a coleta (+ selenium)                                            ← novo
```

## O caminho da coleta dinâmica

```
robots.txt → abrir o Chrome → driver.get() → ESPERAR a condição (9 UFs)
          → page_source → snapshot → BeautifulSoup → guarda → CSV      (driver.quit() no finally)
```

**Medido no TerraBrasilis (23/09/2026, duas execuções):** o `get()` volta em **~1,5 s** — com a
`<table>` já no DOM e **0 linhas**; as **9 UFs e 342 linhas** chegam **~1 s depois**, todas de uma
vez. Coleta completa, com a abertura do Chrome: **~7 s**.

| Estratégia de espera (mesma página, ao vivo) | Tempo | Linhas |
|---|---:|---:|
| sem espera | 1,6 s | **0** |
| espera pela `<table>` (a 1ª versão) | 1,4 s | **0** |
| `time.sleep(5)` | 7,0 s | 342 |
| espera implícita + `find_elements` das linhas | 2,6 s | 342 |
| **espera explícita pela condição (v8)** | **2,6 s** | **342** |

> A implícita **funcionou aqui por sorte**: as linhas chegam todas de uma vez. Na página de exercício
> do passo 3, onde elas chegam uma a uma, a implícita devolve **1 de 9** — sem erro nenhum.

## A rota que não usamos (e por quê)

A aba **Rede** do navegador mostra que a página baixa `…/files/rates2025.json` — valores por
**código** de UF, traduzidos por um segundo arquivo. É mais rápido. **Não usamos** porque é interno ao
app do INPE: sem documentação, com o **ano no nome do arquivo** e códigos que pedem tradução. As duas
rotas dão **os mesmos 342 números** (conferido em `../../aula-10-step-by-step/passo05_a_escada.py`).
**No seu projeto, se houver um JSON assim estável, prefira-o** — o TP3 pede *"manter a simplicidade
quando possível"*.

## Publicar

```bash
python -m src.coleta_dinamica      # coleta fresca (na sua máquina)
git add .
git commit -m "v8: desmatamento por UF (PRODES/INPE), página dinâmica coletada com Selenium"
git push
```

O CSV sobe; o Selenium não. O rodapé da barra lateral mostra `v8 — Aula 10 (página dinâmica coletada
com Selenium)`.

## Licença da fonte nova

**CC BY-SA 4.0** (TerraBrasilis): cite **e** compartilhe igual. O CSV que a página Desmatamento
deixa baixar é derivado — herda a mesma licença, e a legenda da página diz isso.

## Verificação

Confirmado em 23/09/2026 — coleta real no TerraBrasilis (Selenium 4.49, Chrome 153 *headless*),
`AppTest` (Streamlit 1.61) e Chrome *headless* sobre o app:

| Afirmação | Verificação |
|---|---|
| O `requests` recebe uma casca | 3.098 bytes; texto visível `'TerraBrasilis'` (13 caracteres); 0 tabelas |
| Coleta completa | **342 linhas · 9 UFs · 1988–2025 · 6,6–6,8 s** |
| Extração correta | Selenium × JSON da própria página: **342 × 342, zero diferenças** |
| Números batem com o PRODES publicado | 2004 = 27.772 km² · 2023 = 9.064 · 2024 = 6.518 · pico 1995 = 29.059 |
| Guarda funciona | espera pela `<table>` → 0 linhas → **"NÃO gravei"**, coleta anterior preservada |
| Reprocessar sem rede | `--do-snapshot` → as mesmas 342 linhas |
| As sete páginas rodam, inclusive pelo link direto | `AppTest`, sessão nova direto em cada uma: zero exceções |
| Filtros da página nova sobrevivem à troca de página | PA+MT+AM, 2010–2025 → Notícias → volta: mantidos |
| O app não depende do Selenium | nenhuma página importa `selenium`; só `src/coleta_dinamica.py`, dentro das funções |
