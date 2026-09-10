# Bloco 4 — Extração de conteúdo web para Ciência de Dados
### PB Etapa 4 · Competência 2 · semanas 7 e 8 · entrega: **TP2** (fecha aqui)

**Competência 2:** desenvolver protótipo de aplicação baseada em Streamlit usando dados
provenientes da Web.

| Aula | Subcomp. | Tema | Ideia-força |
|:----:|:--------:|------|-------------|
| [aula-07/](aula-07/) | **2.4** | **Quando não existe API** | permissão → HTML → estrutura → **CSV** |
| [aula-08/](aula-08/) | **2.3 + 2.5** | **O arquivo entra, o arquivo sai** | upload/download → **cache** → estado |

| Subcomp. | O que você deve ser capaz de fazer | Leitura de apoio |
|---------:|-----------------------------------|------------------|
| **2.3** | Desenvolver serviços de **upload e download** de arquivos em Streamlit. | RAGHAVENDRA, cap. **5** |
| **2.4** | **Extrair conteúdo de páginas web** usando as ferramentas propícias. | CHAPAGAIN, *Hands-On Web Scraping with Python*, 2ª ed., cap. **5** |
| **2.5** | Utilizar **cache e estado de sessão** em Streamlit para performance e persistência. | RAGHAVENDRA, cap. **8** |

## O arco do bloco

A Aula 7 resolve o caso em que **a fonte não tem API**: pedir permissão (`robots.txt`), baixar,
estruturar com BeautifulSoup e gravar um CSV. A Aula 8 fecha o ciclo do arquivo — o usuário
**envia** o dele, **leva** o seu embora — e separa as duas memórias do Streamlit: **cache** (o que
vale para todos) × **estado de sessão** (o que é de quem está olhando).

> **A coleta não é um recurso do app.** A partir daqui o `app.py` **não raspa**: ele lê o que a
> coleta gravou em `data/processed/`. Rode `python -m src.coleta_web` antes de `streamlit run app.py`.
> Os HTMLs brutos não vêm no repositório (é conteúdo de terceiros e é regenerável) — a coleta
> os baixa de novo.

**O TP2 fecha na Aula 8.** O checklist final está na seção 8 do
[`aula-08/student-guide.md`](aula-08/student-guide.md).
