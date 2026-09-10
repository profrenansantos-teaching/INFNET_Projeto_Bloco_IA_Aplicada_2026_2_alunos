# Ambiente (Colab) — o "delta" da Aula 1

> O que muda em relação à `aula-01/` (versão local). O **conteúdo** (problema, CRISP-DM/TDSP, artefatos,
> tipos de dados, Python puro, camadas de profundidade, estudo de caso) é **idêntico**.

## Roda no Colab (sem setup)
- **Dados em Python puro:** ler um CSV com o módulo `csv` → **lista de dicionários** → `len/set/sum`.
  → notebook `aula1_dados_em_python_puro.ipynb`.
- No Colab, em vez de `venv`, usa-se `!pip install ...` (aqui nem precisa — só a biblioteca padrão).

## Fica local
- A **primeira app Streamlit** (`st.title`, `st.dataframe`, `st.metric`): `venv` + `streamlit run app.py`.

## Ajustes no deck (vs. `aula-01/`)
- **+ slide** "Ambiente: onde cada coisa roda" (Colab × local).
- **+ slide** "Abrir no Google Colab" (QR + link).
- **Passo 0** trocado por **"dois ambientes"** (Colab p/ dados · local p/ app).
- Notas marcam **🟦 Dados = Colab** e **💻 App = local**.
