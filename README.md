# Projeto de Bloco: Inteligência Artificial Aplicada — Materiais do Aluno
### Ciência de Dados Aplicada · Faculdade INFNET · 2026/2 (3T26)

Professor: **Renan Santos** · Plano de Ensino: `IAAP01d`

Este repositório reúne **tudo o que você recebe** da disciplina: os slides de cada encontro,
o material de apoio, os passos executáveis e o código do painel que construímos juntos.

---

## O que você vai construir

Um **dashboard interativo em Python com Streamlit** — o **Painel ODS Brasil** — que integra
**WebScraping, APIs e LLMs**, aplicando métodos de gestão de projetos data-driven
(**CRISP-DM** e **TDSP**). O fio condutor dos trabalhos práticos são **soluções sustentáveis
alinhadas a ESG e à Agenda 2030 (ODS)**.

O painel cresce a cada aula. Cada pasta `demo/painel_ods_brasil/` é uma **versão** dele, e o
`README.md` de dentro lista exatamente **o que mudou da versão anterior e por quê** — é a melhor
forma de ver a progressão.

---

## Mapa das aulas

| Aula | Pasta | Tema | Etapa do PB | Entrega |
|:----:|-------|------|:-----------:|:-------:|
| **1** | [aula-01/](aula-01/) · [aula-01-colab/](aula-01-colab/) | Introdução ao planejamento de projeto de Ciência de Dados | 1 | TP1 |
| **2–3** | [aula-02/](aula-02/) · [aula-02-colab/](aula-02-colab/) | Coleta e visualização de dados com Python e Streamlit | 2 | TP1 |
| **5** | [bloco-03/aula-05/](bloco-03/aula-05/) | Do meu computador para a internet (ambiente, Git, deploy) | 3 | TP2 |
| **6** | [bloco-03/aula-06/](bloco-03/aula-06/) | O painel responde ao usuário (widgets, formulário, estado) | 3 | TP2 |
| **7** | [bloco-04/aula-07/](bloco-04/aula-07/) | Quando não existe API (extração de conteúdo web) | 4 | TP2 |
| **8** | [bloco-04/aula-08/](bloco-04/aula-08/) | O arquivo entra, o arquivo sai (upload/download, cache, estado) | 4 | TP2 |

> As aulas 1 e 2 têm uma **versão paralela para Google Colab** (pastas `-colab`): o mesmo conteúdo,
> com a parte de dados rodando no navegador, sem instalar nada. O **app Streamlit** continua local.

---

## O que tem dentro de cada pasta de aula

| Arquivo / pasta | Para quê |
|-----------------|----------|
| `student-guide.md` | **Comece por aqui.** O material de apoio: o que ler antes, a cola de código da aula, os erros comuns e o checklist do TP. |
| `PB_IA_Aplicada_AulaXX_slides.pptx` | O deck completo da aula (versão de referência, com os slides extras). |
| `Aula XX-DDMMM2026.pdf` | Os slides **como foram apresentados** em sala, em PDF. |
| `aula-XX-step-by-step/` | Os **passos executáveis**: um arquivo por conceito, que roda sozinho e explica no `print` o que acabou de acontecer. Tem um `README.md` com a ordem recomendada. |
| `demo/painel_ods_brasil/` | O **código do painel** na versão daquela aula, rodável. |

---

## Como rodar o código

Você precisa de **Python 3.12+**. Em qualquer pasta `demo/painel_ods_brasil/`:

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows  ·  source .venv/bin/activate no macOS/Linux
pip install -r requirements.txt
streamlit run app.py
```

Os passos executáveis rodam do mesmo jeito, um por vez:

```bash
cd aula-02/aula-02-step-by-step
python passo01_chamada_basica.py
```

**Sem internet ou com a API bloqueada?** Quase todos os passos funcionam offline: eles leem
respostas reais já salvas em JSON (pastas `dados/` e `data/sample/`). Os `README.md` de cada pasta
dizem quais passos precisam de rede.

A partir da Aula 7, a **coleta** é uma etapa separada do app — rode-a antes:

```bash
python -m src.coleta_web     # coleta e grava em data/processed/
streamlit run app.py         # o app lê o que a coleta gravou
```

---

## Bibliografia de apoio

Os livros de referência da disciplina são indicados no Plano de Ensino e estão disponíveis na
**biblioteca virtual da INFNET**. Eles **não** são distribuídos aqui — são material protegido por
direitos autorais. Os guias de cada aula citam capítulo e página (ex.: `[Richards, p174]`) para
você ir direto ao ponto.

---

## IA como copiloto

Usar IA generativa para programar é **encorajado** nesta disciplina — com uma condição que vale
para toda entrega: **você precisa entender o que foi gerado e saber explicar as decisões**. O
`student-guide.md` da Aula 1 tem a seção com as regras e bons prompts.

---

## Dúvidas

Traga para a aula ou use o canal da turma. Se um comando não funcionar, copie a **mensagem de erro
inteira** — ela é metade do diagnóstico.

---
Materiais da disciplina · uso didático · © Renan Santos / INFNET
