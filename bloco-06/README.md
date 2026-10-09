# Bloco 6 — Desenvolvimento de APIs com FastAPI
### PB Etapa 6 · Competência 3 · entrega: **TP3** (fecha aqui)

**Competência 3:** integrar aplicação com múltiplas páginas com dados provenientes de APIs
personalizadas.

| Aula | Subcomp. | Tema | Ideia-força |
|:----:|:--------:|------|-------------|
| [aula-11/](aula-11/) | **3.3** (+3.4) | **Do outro lado da API** | o painel é uma casca para programas → o ambiente → **o tipo é a guarda** → caminho × consulta |
| aula-12 *(em breve)* | **3.4** | **Quem recebe, valida** | POST + modelo → recusar em voz alta → guardar → routers → o painel como cliente da API |

| Subcomp. | O que você deve ser capaz de fazer | Leitura de apoio |
|---------:|-----------------------------------|------------------|
| **3.3** | Configurar o ambiente para o desenvolvimento de APIs com **FastAPI**. | ADESHINA, *Building Python Web APIs with FastAPI*, cap. **1** |
| **3.4** | Construir **rotas e endpoints** em uma aplicação simples usando FastAPI. | ADESHINA, cap. **2** |

## O arco do bloco

Desde a Aula 2 o painel **consome** APIs (a do IBGE). Neste bloco ele passa a **oferecer** a sua: o
painel é para pessoas; a API, para programas — e, para um programa, o painel Streamlit é uma **casca**
(*"You need to enable JavaScript to run this app."*). A Aula 11 monta o ambiente e as rotas de
**consulta** (GET); a Aula 12, o **envio** (POST, com validação), a organização em módulos e a
integração com o painel.

> **O livro é de 2022.** Ele escreve as rotas com `async def`, mostra só o Unix e usa o Pydantic 1. O
> curso usa `def`, o Windows e o Pydantic 2 — e os `student-guide.md` dizem, com página, onde o livro e o
> FastAPI de hoje divergem.

## Avisos práticos

**Dois terminais, os dois na pasta do projeto** (`demo/painel_ods_brasil/`):

| Terminal 1 — o painel | Terminal 2 — a API |
|---|---|
| `streamlit run app.py` | `uvicorn api.main:app --reload` |
| http://localhost:8501 | http://127.0.0.1:8000/docs |

- **`python api/main.py` não sobe nada** — quem serve a API é o `uvicorn`. E rodá-lo de dentro de `api/`
  dá `No module named 'src'`.
- **O `/docs` precisa de internet no navegador** (ele baixa o Swagger). A API funciona sem.
- **No Windows PowerShell 5.1, `curl` não é o curl:** use `curl.exe`, o navegador, o `/docs` ou o
  `requests`.
- **Porta 8000 ocupada?** Pare o servidor anterior com **Ctrl+C**. Se ele ficou órfão:
  `netstat -ano | findstr :8000` e `taskkill /PID <número> /F`.

**O TP3 fecha neste bloco.** O checklist do item 4 (parte 1) está na seção 10 do
[`aula-11/student-guide.md`](aula-11/student-guide.md); o checklist completo vem com a Aula 12.
