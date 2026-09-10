# Painel de Indicadores Sustentáveis do Brasil — estado da Aula 2

Evolução do projeto: a amostra manual da Aula 1 dá lugar à **coleta real via API do IBGE**
(Python puro: `requests` + `json`, **sem pandas**), com **cache/fallback**, `@st.cache_data`,
filtro por região e **visualizações**.

## Estrutura
```
painel_ods_brasil/
├── app.py                     # interface Streamlit (filtro, métricas, gráfico, tabela)
├── requirements.txt           # streamlit + requests
├── data/
│   └── sample/
│       ├── populacao_amostra.csv   # amostra da Aula 1
│       └── ufs_cache.json          # cache das 27 UFs (fallback)
├── docs/  (project_charter.md · data_summary_report.md)
└── src/
    ├── __init__.py
    └── data_access.py         # coleta via API do IBGE (isolada da interface)
```

## Como executar
```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate   |  Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Novidades da Aula 2 (vs Aula 1)
- **Coleta via API** (`src/data_access.py`) — JSON (semi) → lista de dicionários (tabela).
- **Cache/fallback** — se a API cair, usa `data/sample/ufs_cache.json` (robustez em sala).
- **`@st.cache_data`** — não recoleta a cada interação.
- **Interatividade** — filtro por região (`st.multiselect`) e **gráfico** (`st.bar_chart`).
- **Separação de camadas** — dados (`src/`) isolados da interface (`app.py`).

Testado: `python src/data_access.py` coleta 27 UFs ao vivo; `streamlit run app.py` roda sem erro.
