# Painel de Indicadores Sustentáveis do Brasil — v7

Demo do **Projeto de Bloco: Inteligência Artificial Aplicada** (INFNET) · **Aula 9 · PB Etapa 5**.

Painel ESG/ODS em **Python puro** (sem pandas). Esta versão (**v7**) abre a **Competência 3** e o
**TP3**: o painel, que tinha virado **uma página de 360 linhas**, passa a ter **menu de navegação e
seis páginas** — uma para cada pergunta do usuário. **Nenhuma dependência nova**: `st.navigation`
e `st.Page` fazem parte do Streamlit.

## Rodar localmente

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows  ·  source .venv/bin/activate no macOS/Linux
pip install -r requirements.txt

python -m src.coleta_web          # 1) COLETA (Aula 7, roda à parte) -> data/processed/
streamlit run app.py              # 2) USO — o arquivo principal continua sendo app.py
```

## O que mudou da v6 para a v7

| # | Mudança | Ferramenta | Por quê |
|---|---------|-----------|---------|
| 1 | `app.py` virou um **roteador** de ~50 linhas | `st.navigation` | configura, prepara a memória e define o menu — não desenha análise |
| 2 | **Seis páginas**, agrupadas em três seções do menu | `st.Page(title=, icon=)` | uma pergunta, uma página |
| 3 | Links entre páginas no conteúdo | `st.page_link` | a página Início é um índice das perguntas |
| 4 | Leituras caras **definidas uma vez**, importadas por todas | `comum.py` + `@st.cache_data` | uma definição, um cache |
| 5 | Memória **inicializada no roteador** | `st.session_state.setdefault` | o link direto de qualquer página não quebra |
| 6 | Filtros **preservados** entre páginas | `preservar_filtros()` | sem isso, voltavam ao padrão a cada troca de página |
| 7 | Página **Dados e método** | — | fontes + licenças + cache medido + a memória da sessão, na tela |

## Estrutura

```
painel_ods_brasil/
├── app.py                 ROTEADOR   — set_page_config, memória comum, st.navigation   ← reescrito
├── comum.py               COMUM      — leituras cacheadas, estado, filtros preservados ← novo
├── paginas/                                                                            ← novo
│   ├── inicio.py          🏠 o problema + o que cada página responde (st.page_link)
│   ├── indicadores.py     📊 filtros, métricas, gráfico, tabela, download
│   ├── comparador.py      ⭐ UFs marcadas — o estado atravessa páginas
│   ├── noticias.py        📰 coleta + envio de CSV + download
│   ├── palavras.py        🔤 contagem de palavras (a "nuvem" do TP2)
│   └── sobre.py           ℹ️ fontes, licenças, cache medido, memória da sessão
├── src/                   COLETA · DADOS · LÓGICA — inalterados, sem Streamlit
├── data/processed/        o que o app lê (VERSIONADO)
├── docs/                  Project Charter (revisado para o TP3) · Data Summary Report
└── requirements.txt · .gitignore · DEPLOY.md · .streamlit/
```

## Como um app multipáginas roda (a ideia da aula)

> A cada rerun o Streamlit roda o **roteador** inteiro; em `pagina.run()`, roda **só a página
> escolhida**. Trocar de página é um rerun como outro qualquer.

| O que está… | …acontece | Neste app |
|---|---|---|
| no **roteador**, antes de `.run()` | em **toda** página | `set_page_config`, `inicializar_estado()`, `preservar_filtros()`, o menu, o rodapé da barra lateral |
| numa **página** | só quando ela é a escolhida | a análise e os widgets daquela pergunta |
| em **`comum.py`** | quando alguma página chama | `obter_dados()`, `obter_noticias()`, `contar_palavras()` |

## Os dois tropeços da v7 (reais)

**1. O filtro que esquecia.** No rerun em que um widget com `key` **não é desenhado**, o Streamlit
**apaga** a chave dele do `st.session_state`. Sair de *Indicadores* é esse rerun — e os quatro
filtros voltavam ao padrão. Correção em `comum.py :: preservar_filtros()`, chamada pelo roteador.

**2. O link direto que quebrava.** Com a inicialização dentro de uma página, abrir o endereço direto
de **outra** (`/comparador`) dava `AttributeError: st.session_state has no attribute "favoritas"`.
Pela porta da frente funcionava — por isso ninguém via. Correção: a memória nasce no **roteador**.

> Os dois estão reproduzidos, com interruptor, em `../aula-09-step-by-step/passo03_estado_entre_paginas/`.

## O roteiro de demonstração

1. em **Indicadores**, filtre só o *Nordeste* e aplique;
2. em **Comparador**, marque **SP** e **BA** → o aviso diz que SP está fora do filtro que você deixou
   em Indicadores (uma página lendo o que o usuário fez na outra);
3. vá a **Notícias** e volte → o filtro **continua** *Nordeste*;
4. abra **Dados e método** → *A memória desta sessão* mostra tudo o que você fez nas outras páginas.

## Publicar

O **arquivo principal continua sendo `app.py`**: o contrato de quatro itens do Community Cloud
(Aula 5) não mudou, e nada precisa ser reconfigurado no painel do serviço.

```bash
git add .
git commit -m "v7: aplicação multipáginas com menu de navegação"
git push
```

O rodapé da barra lateral mostra `v7 — Aula 9 (aplicação multipáginas)`.

## Verificação

Confirmado por `AppTest` (Streamlit 1.61) e em navegador real (Chrome 153, *headless*), em 23/09/2026:

| Afirmação | Verificação |
|---|---|
| As seis páginas rodam sem exceção | navegação por todas, em sequência |
| **Link direto** de cada página funciona | sessão nova aberta direto em cada uma das seis: nenhuma exceção |
| Filtros sobrevivem à troca de página | *Nordeste* + tabela desligada → Notícias → volta: **Nordeste**, 9 UFs, sem tabela |
| Estado atravessa páginas | SP e BA marcados no Comparador aparecem em **Início** e em **Dados e método** |
| Uma página lê o que o usuário fez na outra | Comparador avisa: *"fora do filtro que você deixou em Indicadores: SP"* |
| A coleta do IBGE roda **uma vez** para todas as páginas | *Custo NESTE rerun* = **0 ms** em Dados e método depois de passar por Início |
| Remover o envio limpa a seleção de seções | seção enviada sai das opções e da seleção, sem exceção |
