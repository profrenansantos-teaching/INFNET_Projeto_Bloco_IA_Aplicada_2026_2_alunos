# Painel de Indicadores Sustentáveis do Brasil

Projeto-demonstração do **Projeto de Bloco: IA Aplicada** (INFNET). Construído ao vivo,
etapa a etapa. Estado atual: **Aula 1** — app demo com amostra de dados.

## Estrutura de diretórios (organizada pelo ciclo de vida TDSP)
```
painel_ods_brasil/
├── app.py                     # aplicação Streamlit (ponto de entrada)
├── requirements.txt           # dependências do projeto
├── data/
│   ├── raw/                   # dados brutos coletados (Aquisição de Dados)
│   ├── processed/             # dados tratados (Preparação)
│   └── sample/                # amostra manual usada na Aula 1
├── docs/
│   ├── project_charter.md     # artefato TDSP: escopo, metas, stakeholders
│   └── data_summary_report.md # artefato TDSP: fontes de dados
└── src/
    └── data_access.py         # coleta via API do IBGE (implementado na Aula 2)
```

## Como executar
```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
A aplicação abre em `http://localhost:8501`.

## Roadmap do projeto (Etapas do PB)
- **Aula 1 ✅** — planejamento (Charter, Data Summary), app demo com amostra.
- **Aula 2** — coleta real via API do IBGE (27 UFs) + visualizações interativas.
- Próximas — WebScraping, FastAPI, integração com LLMs.
