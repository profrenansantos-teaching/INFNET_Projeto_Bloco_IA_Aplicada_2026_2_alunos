# Aula 2 — Versão Google Colab
### Coleta e visualização de dados · trilha "Colab para dados + Streamlit local"

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/profrenansantos-teaching/INFNET_Projeto_Bloco_IA_Aplicada_2026_2_alunos/blob/main/aula-02-colab/aula2_coleta_via_api.ipynb)

> **Versão paralela (em avaliação).** Mesmo **conteúdo conceitual** da `aula-02/` (fontes/tipos, API REST,
> anti-padrões, princípios, estudo de caso v2) — muda apenas o **ambiente/execução**.

## O que tem aqui
| Arquivo | O quê |
|---------|-------|
| `aula2_coleta_via_api.ipynb` | Notebook Colab: coleta das 27 UFs via API do IBGE, exploração e gráfico (Python puro) |
| `PB_IA_Aplicada_Aula02_Colab_slides.pptx` | Deck com os slides de ambiente adaptados (Colab × local) + slide "Abrir no Colab" (QR) |
| `AMBIENTE-COLAB.md` | O que roda no Colab × o que fica local (o "delta" desta versão) |

Para o **material de apoio**, o deck e o demo da versão local, use os arquivos da pasta
**`../aula-02/`** — o conteúdo é o mesmo; aqui só troca o ambiente.

## Onde cada coisa roda
- **Google Colab** → a **coleta e a manipulação** de dados (o notebook). Zero setup.
- **Local** (ou Streamlit Community Cloud) → o **app Streamlit** (`streamlit run app.py`), que é o entregável do TP1.
  O Colab não roda um servidor Streamlit sem túnel — por isso o app fica local.

## Como abrir o notebook
- **Badge acima** — este repositório é público, o Colab abre o notebook direto; ou
- **Colab → Arquivo → Fazer upload de notebook** e envie o `.ipynb`.
