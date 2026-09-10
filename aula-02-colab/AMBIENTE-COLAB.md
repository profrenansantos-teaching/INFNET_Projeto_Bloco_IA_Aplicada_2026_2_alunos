# Ambiente (Colab) — o "delta" da Aula 2

> O que muda em relação à `aula-02/` (versão local). O **conteúdo** (API REST, coleta, JSON, visualização,
> anti-padrões, princípios, caso v2) é **idêntico**.

## Roda no Colab (sem setup)
- **Coleta via API** (`requests` + `json`), navegação do JSON aninhado, **lista de dicionários**,
  `len/set/sum`, filtro. → notebook `aula2_coleta_via_api.ipynb`.
- No Colab, em vez de `venv`, usa-se `!pip install requests` (na prática, já vem instalado).

## Fica local (ou Streamlit Community Cloud)
- O **app Streamlit** (`@st.cache_data`, `st.multiselect`, `st.bar_chart`, `st.dataframe`): `streamlit run app.py`.
- O código de **coleta é o mesmo** — migra do notebook para `src/data_access.py` do projeto local.

## Ajustes no deck (vs. `aula-02/`)
- **+ slide** "Ambiente: onde cada coisa roda" (Colab × local).
- **+ slide** "Abrir no Google Colab" (QR + link).
- Notas das seções marcam **🟦 Coleta = Colab** e **💻 Visualização = local**.

## Mapa de execução da aula
| Bloco | Onde roda |
|-------|-----------|
| Fontes/tipos + API REST (conceito) | — (exposição) |
| **Coleta via API** (código) | **Colab** (notebook) |
| **Visualização + robustez** (app) | **Local** (Streamlit) |
