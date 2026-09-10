# Aula 2 — Material de Apoio do Aluno
### Coleta e visualização de dados com Python e Streamlit

Hoje o painel deixa de usar amostra: vamos **coletar dados de verdade** (API do IBGE) e **mostrá-los**. 🌱

> **Padrão do bloco:** Python puro (`requests`+`json`, **sem pandas**); dados como **lista de dicionários**;
> **IA como copiloto** (entender e explicar). A coleta fica **isolada** da interface.

## Antes da aula — o que ler (≈ 35 min)
| Leitura | Por quê | Foque em |
|---------|---------|----------|
| ESPPENCHUTZ, cap. 2 ("Retrieving data using API authentication") | coleta via API | `requests.get`, `.json()`, status; "não hardcode a chave" (p70) |
| ESPPENCHUTZ, cap. 4 ("Reading CSV and JSON") | JSON | como um JSON vira objetos Python |
| RAGHAVENDRA, cap. 3 e 5 | visualização/widgets | `st.bar_chart`, `st.multiselect` |

**Perguntas-guia:** (1) O que é um endpoint e um método GET? (2) Por que uma API pode ser melhor que baixar
um arquivo? (3) O que significa status 200? (4) Como transformar um JSON aninhado em tabela?

## Em aula — o arco
Recap (v1) → fontes/tipos + **API REST** → **coleta via API** (código guiado) → **visualização + robustez**
(código guiado) → princípios + fecho. Traga o projeto da Aula 1.

## Conceitos-chave
- **3 formas de obter dados:** **arquivo** (estático/bulk) · **API** (atualizado/integrável) · **WebScraping**
  (quando não há API). O IBGE tem **API pública** → é a nossa escolha.
- **API REST:** pedir por **URL (endpoint)** com **GET** e **parâmetros**; receber **JSON** + **status**
  (200 ok · 404 não achado · 500 erro do servidor).
- **JSON (semi-estruturado) → tabela (lista de dicionários):** navegar o JSON aninhado e montar 1 dict/linha.
- **Robustez:** `@st.cache_data` (não recoletar) + **fallback** (cache local se a API cair).
- **Separação de camadas:** dados em `src/` ≠ interface em `app.py`.

## Cola de código — coleta + visualização (Python puro)
```python
# ---- src/data_access.py : coleta (isolada da interface) ----
import requests, json
from pathlib import Path

def coletar():
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados?orderBy=nome"
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()               # erro se status != 2xx
    return resp.json()                    # JSON -> lista de dicionários
```
```python
# ---- app.py : interface (Streamlit) ----
import streamlit as st
from src.data_access import carregar_dados

@st.cache_data(ttl=3600)                  # não recoletar a cada clique
def obter_dados():
    return carregar_dados()

dados, fonte = obter_dados()
st.caption(f"Fonte: {fonte}")

regioes = sorted({l["regiao"] for l in dados})
sel = st.multiselect("Região", regioes, default=regioes)
filtrados = [l for l in dados if l["regiao"] in sel]

st.bar_chart(sorted(filtrados, key=lambda l: -l["populacao_2025"]), x="uf", y="populacao_2025")
st.dataframe(filtrados, use_container_width=True, hide_index=True)
```
**Dicas:** `raise_for_status()` evita seguir com erro; `@st.cache_data` evita "martelar" a API;
`st.bar_chart` aceita **lista de dicionários** (sem pandas).

## IA como copiloto
Peça à IA para explicar um JSON aninhado ou gerar a navegação — mas **entenda e saiba explicar** cada `[...]`.

## Checklist do TP1 (parte desta aula)
- [ ] Coleta via **API** implementada e **isolada** em `src/` (com `raise_for_status`).
- [ ] JSON transformado em **lista de dicionários** (tipos tratados).
- [ ] **Cache/fallback** para robustez.
- [ ] **Gráfico** + **filtro** no Streamlit mostrando os dados coletados.

## Autoteste
1. Diferença entre API, arquivo e WebScraping — quando usar cada?
2. O que `resp.raise_for_status()` faz?
3. Por que usar `@st.cache_data` na função de coleta?
4. `st.bar_chart` precisa de pandas?
5. Por que a chave de uma API **não** deve ficar hardcoded no código?

<details><summary>Respostas</summary>

1. API = dado atualizado/integrável; arquivo = estático/bulk; scraping = quando não há API (frágil).
2. Levanta um erro se o status HTTP não for 2xx (evita seguir com uma resposta de erro).
3. Para **não recoletar** a cada interação (rápido; não "martela" a API).
4. **Não** — aceita lista de dicionários com `x=`/`y=`.
5. Porque é **segredo**: se versionado, vaza e pode gerar custo/abuso (segurança).
</details>
