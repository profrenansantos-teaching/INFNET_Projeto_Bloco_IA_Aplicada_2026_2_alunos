# Bloco 8 — LLM e integração com FastAPI
### PB Etapa 8 · Competência 4 · **TP4**, itens 1 e 2 — **fecha o TP4** (entrega na semana de 16–21/11)

**Competência 4:** implementar uma API com FastAPI integrada com modelos LLMs.

As duas aulas desta etapa couberam em **um encontro** (05/11). Por isso o bloco tem três pastas — comece pela primeira:

| Pasta | Subcomp. | Tema | O que tem |
|-------|:--------:|------|-----------|
| [aula-15-16/](aula-15-16/) | **4.3 + 4.4** | **Quem escolhe, mede; quem pesa, carrega uma vez** | **Comece por aqui:** os slides em PDF, o [mapa da aula](aula-15-16/student-guide.md) e [todos os passos](aula-15-16/aula-15-16-step-by-step/) |
| [aula-15/](aula-15/) | **4.3** | **Quem escolhe, mede** | o [guia completo](aula-15/student-guide.md) da escolha do modelo e o painel **v13** |
| [aula-16/](aula-16/) | **4.4** | **Quem pesa, carrega uma vez** | o [guia completo](aula-16/student-guide.md) da integração e o painel **v14**, o do fim da aula |

| Subcomp. | O que você deve ser capaz de fazer | Leitura de apoio |
|---------:|-----------------------------------|------------------|
| **4.3** | Identificar e escolher o **modelo LLM** adequado para uma aplicação com base em critérios de desempenho, custo e acessibilidade. | ALTO, *Building LLM Powered Applications*, cap. **3** |
| **4.4** | Integrar modelos LLM do repositório **HuggingFace** com FastAPI para processamento de linguagem natural nas aplicações. | PARANDEH, *Building Generative AI Services with FastAPI*, cap. **3** |

## O arco do bloco

No Bloco 7, a rota do TP4 ganhou um contrato e os seus erros, com um motor provisório de regras. Agora entra o modelo de
verdade, em dois tempos. A **v13** escolhe, **medindo**: a ficha do modelo no Hub, antes de baixar; o custo em memória e
em tempo; o banco de provas com 30 relatos rotulados; e a justificativa por escrito, que é o item 1 do TP4. A **v14**
integra: carrega o modelo **uma vez**, no `lifespan`; atende numa rota **`def`**, para não travar a API; lê do disco com
`local_files_only`; responde **503** se o modelo faltar; e **pontua** as categorias do contrato, em vez de deixar o
modelo escrever o que quiser. O contrato da Aula 13 não mudou — trocou-se só o motor.

> **O livro não cobre tudo.** Nenhum dos dois trata de CPU, de português, de medir na própria máquina, de
> `local_files_only` nem de 503 do modelo. Os [guias](aula-15/student-guide.md) dizem, com página, o que veio do livro e
> o que foi medido no lugar.

## ⚠️ Antes de rodar: o download, uma vez

Esta é a primeira etapa com arquivos grandes fora do repositório: os **pesos dos modelos**, que ficam no cache do Hugging
Face, na sua pasta de usuário.

| O quê | Tamanho | Comando (com internet, em casa) |
|-------|--------:|---------------------------------|
| as bibliotecas (`transformers`, `torch`, `huggingface_hub`) | ~0,5 GB | `pip install -r requirements-api.txt`, da pasta do demo |
| os dois modelos dos passos | ~1,5 GB | `python passo00_baixar.py`, da [pasta dos passos](aula-15-16/aula-15-16-step-by-step/) |
| o modelo do demo (v14) | 3,1 GB | `python -m src.baixar_modelo`, da pasta do demo |

- **No Linux**, instale antes o `torch` de CPU: `pip install torch --index-url https://download.pytorch.org/whl/cpu`. O
  pacote padrão traz a CUDA da NVIDIA, com vários GB. No Windows e no Mac, o `pip` já traz o de CPU.
- **Memória:** o modelo do demo pede ~6,5 GB livres; os passos rodam com ~2 GB.
- **Crie um ambiente novo** para esta etapa, de preferência **fora de pastas sincronizadas** (Google Drive, OneDrive): o
  `torch` tem milhares de arquivos.

## Avisos práticos

- **Os avisos do [Bloco 6](../bloco-06/README.md) continuam valendo:** dois terminais, `curl.exe`, porta ocupada, o 404
  na raiz dos passos.
- **Cada aula tem os seus passos 1 a 5.** `passo01_pipeline.py` é o passo 1 da Aula 15; `passo01_por_requisicao.py`, o da
  Aula 16. O [`README.md` da pasta](aula-15-16/aula-15-16-step-by-step/README.md) dá a ordem.
- **As APIs desta etapa sobem sem `--reload`:** o modelo é pesado, e cada reinício o carrega de novo.
- **Uma coisa pesada por vez.** Feche um passo da Aula 16 antes de subir o demo.
- **Os tempos são da sua máquina.** As contagens (acertos, erros) não mudam; os segundos, sim. Meça e anote a máquina.

**O TP4 completo:** o checklist está na seção 4 do [`aula-15-16/student-guide.md`](aula-15-16/student-guide.md).
