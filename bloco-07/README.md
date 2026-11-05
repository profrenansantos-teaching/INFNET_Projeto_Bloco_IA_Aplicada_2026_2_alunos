# Bloco 7 — Manipulação de APIs e tratamento de erros em FastAPI
### PB Etapa 7 · Competência 4 · **TP4**, itens 2, 3 e 4 (entrega na semana de 16–21/11)

**Competência 4:** implementar uma API com FastAPI integrada com modelos LLMs.

As duas aulas desta etapa couberam em **um encontro** (29/10). Por isso o bloco tem três pastas — comece pela primeira:

| Pasta | Subcomp. | Tema | O que tem |
|-------|:--------:|------|-----------|
| [aula-13-14/](aula-13-14/) | **4.1 + 4.2** | **Quem responde, promete; quem falha, explica** | **Comece por aqui:** os slides em PDF, o [mapa da aula](aula-13-14/student-guide.md) e [todos os passos](aula-13-14/aula-13-14-step-by-step/) |
| [aula-13/](aula-13/) | **4.1** | **Quem responde, promete** | o [guia completo](aula-13/student-guide.md) das respostas e o painel **v11** |
| [aula-14/](aula-14/) | **4.2** | **Quem falha, explica** | o [guia completo](aula-14/student-guide.md) dos erros e o painel **v12**, o do fim da aula |

| Subcomp. | O que você deve ser capaz de fazer | Leitura de apoio |
|---------:|-----------------------------------|------------------|
| **4.1** | Manipular as respostas de APIs utilizando **Response Models** para garantir consistência nos retornos. | ADESHINA, *Building Python Web APIs with FastAPI*, cap. **3** |
| **4.2** | Tratar erros de API de forma robusta, utilizando **exceções HTTP** em FastAPI. | ADESHINA, cap. **3** |

## O arco do bloco

No Bloco 6, a API aprendeu a **receber** — e a validar o que recebe. Agora ela aprende a **responder**. A **v11**
declara o que devolve (`response_model`) e ganha a rota do TP4, `POST /processar_texto`, com o contrato pronto antes do
motor. A **v12** diz o que deu errado, com o status certo e uma frase: **404** (o que se pediu não existe), **409** (o
pedido conflita com o que já existe), **503** (falta algo no servidor) e um **500 em JSON, com código**, para o que
ninguém previu. E o painel passa a ler as respostas **pelo status**.

> **O motor de análise ainda é provisório:** regras de palavras-chave, em `data/analisador/regras.json`. Ele existe para
> que a rota tenha contrato e erros antes do LLM. Na Etapa 8, troca-se só o motor; a rota e os modelos ficam.

> **O livro não cobre tudo.** O cap. 3 ensina o *response model*, o `HTTPException` e o 201, mas não fala de 422, 503,
> `exception_handler`, `JSONResponse` nem `responses=`. E o [guia da Aula 13](aula-13/student-guide.md) diz, com página,
> onde ele e o FastAPI de hoje divergem.

## Avisos práticos

- **Os avisos do [Bloco 6](../bloco-06/README.md) continuam valendo:** dois terminais, `curl.exe`, porta ocupada, o 404
  na raiz dos passos.
- **Cada aula tem os seus passos 1 a 5.** `passo01_sem_contrato.py` é o passo 1 da Aula 13; `passo01_200_ou_404.py`, o da
  Aula 14. O [`README.md` da pasta](aula-13-14/aula-13-14-step-by-step/README.md) dá a ordem.
- **Deu 500? Olhe o terminal do `uvicorn`.** O cliente só vê *"Internal Server Error"*; o motivo está lá.
- **O passo 3 da Aula 14 pede para renomear `regras_passo03.json`.** Desfaça depois: sem esse arquivo, o motor do passo
  não carrega.

**O TP4 depois desta etapa:** o checklist está na seção 5 do [`aula-13-14/student-guide.md`](aula-13-14/student-guide.md).
