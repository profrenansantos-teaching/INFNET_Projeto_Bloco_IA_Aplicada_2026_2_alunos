# Aula 14 — Material de apoio do aluno
### Quem falha, explica · PB Etapa 7 · subcompetência 4.2 · **TP4, item 4**

> Consulte enquanto faz o TP4, item 4: *"exceções HTTP específicas em FastAPI… (falha ao carregar o modelo, problemas
> com os dados de entrada, ou timeouts)"*, o **503** quando *"o modelo LLM não estiver carregado corretamente"*, e
> *"feedback útil para o usuário final… facilitando o diagnóstico"*. Com esta aula, a **Etapa 7 está completa** — o que
> falta do TP4 (o LLM) está na seção 8.

---

## 1. O status é a primeira palavra da resposta

*"A 400 status code shouldn't be returned for a server error. Likewise, a 200 status code shouldn't be returned for a
failed request operation."* [Adeshina, p62]

Um programa decide o que fazer **antes** de ler o corpo. Se a API diz **200** para o que falhou, o programa nem chega a
ler o resto — e trata o vazio como resposta. (No caso do curso: um ranking de 2026, ano que o PRODES ainda não
publicou, voltou com 200 e zero linhas — e virou *"nenhum desmatamento em 2026"* num relatório.)

| Família | Status | Quer dizer | Quem resolve |
|---------|:------:|------------|--------------|
| 2xx | **200** · **201** | deu certo · deu certo e **criou** | — |
| 4xx | **422** | o pedido não cumpre o contrato (tipo, limite, campo a mais) | quem pediu |
| | **404** | o que se pediu **não existe** | quem pediu |
| | **409** | o pedido está certo, mas **conflita** com o que já existe | ninguém — já está feito |
| 5xx | **503** | falta algo no servidor, **agora** (o modelo não carregou) | quem roda a API |
| | **500** | a API errou — e não previa | quem mantém a API |

---

## 2. `HTTPException`: levantar o erro, com uma frase

*"Errors in FastAPI are handled by raising an exception using FastAPI's HTTPException class."* [Adeshina, p65]

```python
from fastapi import HTTPException, status

@router.get("/ranking/{ano}")
def ranking(ano: int):
    dados = ranking_do_ano(linhas, ano)
    if not dados:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,      # o nome no lugar do número
            detail=f"O PRODES não tem a taxa de {ano}: a série vai de 1988 a 2025.",
        )
    return {...}
```

| Argumento [Adeshina, p66] | Para quê |
|---------------------------|----------|
| `status_code` | o status — use `status.HTTP_404_NOT_FOUND`, `status.HTTP_409_CONFLICT`, `status.HTTP_503_SERVICE_UNAVAILABLE` |
| `detail` | a frase para quem pediu: **o que aconteceu e, quando der, o que fazer** — nunca um traceback |
| `headers` | opcional (ex.: `Retry-After`, quando vale a pena tentar de novo depois) |

O cliente recebe `{"detail": "O PRODES não tem a taxa de 2026: …"}` com o status 404.

### Não existe ≠ vazio (o critério da Aula 11)

| Pedido | Resposta | Por quê |
|--------|:--------:|---------|
| `GET /ranking/2026` · `GET /relatos/99` | **404** | o **caminho identifica** um recurso — que não existe |
| `GET /relatos?uf=AC` (nenhum do Acre) | **200** · `[]` | a **consulta recorta** uma coleção — vazia é a resposta certa |

### 422 × 409

O relato **repetido** é **409**, não 422: o corpo cumpre o modelo — o conflito é com o **estado** (um relato igual já
gravado). O modelo não tem como saber disso; quem sabe é quem guarda. Bom desenho: a regra mora em `src/` (uma exceção
do domínio, `RelatoRepetido`), e a rota a traduz para HTTP.

---

## 3. Declarar os erros: o `/docs` também documenta o que dá errado

Sem declarar, o *Try it out* de um 404 mostra **`404 Undocumented`** — é a figura 3.2 do livro [p68].

```python
class Erro(BaseModel):
    detail: str

@router.get("/ranking/{ano}", response_model=RespostaRanking,
            responses={404: {"model": Erro, "description": "O PRODES não tem a taxa deste ano."}})

app = FastAPI(..., responses={500: {"model": Erro, "description": "Erro interno, com um código."}})   # em toda rota
```

---

## 4. Falhe em pedaços: o 503 do modelo (o exemplo do TP4)

*"Se o modelo LLM não estiver carregado corretamente… a aplicação deve retornar um código de erro adequado (ex: 503
Serviço Indisponível) e uma mensagem explicativa."* — TP4, item 4

```python
try:
    MOTOR = carregar_motor()                   # na Etapa 8: carregar o modelo LLM
except (OSError, ValueError) as falha:         # arquivo ausente, JSON inválido… (na Etapa 8: mais tipos)
    MOTOR = None
    log.error("Motor NÃO carregado — %s", falha)    # o motivo, no terminal

@router.post("/processar_texto", response_model=ResultadoAnalise,
             responses={503: {"model": Erro, "description": "O motor não foi carregado."}})
def processar_texto(pedido: PedidoAnalise):
    if MOTOR is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="O analisador está indisponível: o motor não foi carregado. As outras rotas funcionam.")
    ...
```

⚠️ **Sem o `try`**, uma falha ao carregar derruba a API **inteira** — `uvicorn` não sobe, e nenhuma rota responde
(nem as que não têm nada a ver com o modelo). Falhe em pedaços, não inteira.

---

## 5. A rede de segurança: o 500 que ninguém previu

Sem tratamento, uma exceção imprevista vira um 500 **em texto puro** (*"Internal Server Error"*) — e um cliente que
faz `r.json()` quebra (`JSONDecodeError`).

```python
import logging, uuid
from fastapi import Request
from fastapi.responses import JSONResponse

log = logging.getLogger("uvicorn.error")

def erro_inesperado(request: Request, exc: Exception) -> JSONResponse:
    codigo = uuid.uuid4().hex[:8]
    log.error("Erro inesperado [%s] em %s %s — %s: %s", codigo, request.method, request.url.path,
              type(exc).__name__, exc)
    return JSONResponse(status_code=500,
                        content={"detail": f"Erro interno na API (código {codigo}). Informe o código a quem mantém a API."})

app.add_exception_handler(Exception, erro_inesperado)
```

**Ao usuário, a frase; ao log, o traceback.** O traceback (que o `uvicorn` imprime logo abaixo da sua linha) **nunca**
vai para o cliente. O **código** liga uma ponta à outra: *"facilitando o diagnóstico"* (TP4).

> **IA como copiloto.** Peça a uma IA o tratamento de erros da sua rota. Ela costuma devolver `400` para tudo o que é do
> cliente e `500` para tudo o que é do servidor — e às vezes põe `str(exc)` (o erro técnico) no `detail`. Confira com a
> tabela da seção 1 e com a regra: **a frase vai para o cliente; o traceback, para o log.**

---

## 6. Do outro lado: o cliente que lê pelo status

O `detail` **não** tem sempre o mesmo formato:

| Status | `detail` |
|--------|----------|
| **422** | uma **lista** — um item por campo (`loc`, `type`, `msg`) |
| 404 · 409 · 503 · 500 | uma **frase** |

Um cliente que trata todo erro como 422 (*"para cada item do detail…"*) percorre a frase **letra por letra**:
`TypeError: string indices must be integers`. **O status decide como ler o corpo:**

```python
def mensagens(r):
    if r.status_code == 422:
        return [f"{e['loc'][-1]}: {e['msg']}" for e in r.json()["detail"]]
    try:
        return [r.json()["detail"]]
    except (ValueError, KeyError, TypeError):
        return [f"A API respondeu {r.status_code} sem explicar o motivo."]
```

**E quando nem há resposta:**

| Exceção do `requests` | O que aconteceu | Para o usuário |
|-----------------------|-----------------|----------------|
| `ConnectionError` (inclui `ConnectTimeout`) | nem conectou — a API está desligada | *"A API não está no ar."* |
| `ReadTimeout` | conectou, mas a resposta não veio a tempo — um LLM na CPU, na Etapa 8 | *"A API demorou mais de 30 s."* |

⚠️ **Trate `ReadTimeout`, não `Timeout`.** No Windows, recusar uma conexão leva ~2 s (medido); com `timeout=2`, a recusa
chega como `ConnectTimeout` — que é `Timeout` **e** `ConnectionError`. Tratando `Timeout` primeiro, a tela diz
"demorou" a uma API desligada.

**E o tom:** um 409 (o relato já está gravado) e um 503 (o analisador está fora; o resto funciona) são **avisos**; um 422
e um 500 são **erros**. Nunca diga "tente de novo" a um 409.

---

## 7. Anti-padrões desta aula

| Anti-padrão | Por que dói |
|-------------|-------------|
| **200** para o que falhou (a lista vazia de um recurso que não existe) | o cliente lê "zero" como resposta |
| **404** para o filtro vazio | obriga o cliente a tratar como erro uma pergunta bem respondida |
| **422** para o conflito (o repetido) | o pedido estava certo — quem conflita é o estado |
| carregar o modelo sem `try` | uma peça quebrada derruba a API inteira |
| deixar o 500 sair em texto puro | `r.json()` quebra do outro lado |
| o traceback (ou `str(exc)`) no `detail` | expõe caminhos e nomes internos — e não ajuda o usuário |
| o erro **não declarado** no `/docs` | *Undocumented*: quem usa a API descobre no susto |
| o cliente que trata todo erro como 422 | `TypeError` no primeiro 404 |
| "tente de novo" a um 409 · a falha numa legenda | o usuário repete o erro · acredita no que não devia |

---

## 8. O TP4, depois desta aula — a Etapa 7 completa

**O que a Etapa 7 cobre (Aulas 13 e 14):**

- [ ] **Item 2:** `POST /processar_texto` de pé (com um motor provisório)
- [ ] **Item 3:** `response_model` na rota e em **todas** as outras — respostas estruturadas e validadas
- [ ] **Item 4:** exceções HTTP **específicas** — 404, 409, 422 (automático), **503 quando o modelo não carrega**
- [ ] **Item 4:** `detail` com **mensagens claras** — o que aconteceu e o que fazer
- [ ] **Item 4:** o 500 imprevisto em JSON, com um **código** que leva ao log (*"facilitando o diagnóstico"*)
- [ ] **Item 4:** o painel (ou o seu cliente) lendo **pelo status**, com *"feedback útil para o usuário final"* — inclusive
      para a API lenta (`ReadTimeout`) ou desligada
- [ ] os erros **declarados** no `/docs` (`responses=`)

**O que vem:**

- [ ] **Etapa 8 — itens 1 e 2:** o **modelo LLM local** (HuggingFace), escolhido por desempenho, custo computacional e
      acessibilidade, **no lugar** do motor provisório — o contrato, o `try` com o 503 e o `timeout` já estão prontos
- [ ] **Documentação:** a justificativa da escolha do modelo e *"como a integração local foi realizada"*
- [ ] **Entrega:** `nome_sobrenome_PB_TP4.PDF` com o **link do repositório no GitHub** (calendário: semana de 16–21/11)

---

## 9. Fontes

- **ADESHINA, A. A.** *Building Python Web APIs with FastAPI*. Packt, 2022 — cap. 3 (*Error handling*: `HTTPException`,
  p65–66; o 404 no lugar do 200, p66–68; a regra do 200, p62); caps. 5–6 (o 409, p96, p131). **[G3]** — páginas do PDF.
- Documentação oficial do FastAPI — `responses=`, `add_exception_handler`, `JSONResponse`; do `requests` —
  `ReadTimeout`, `ConnectionError`. Verificados por execução (FastAPI 0.142, Pydantic 2.13, uvicorn 0.52, Streamlit
  1.61), em 27/10/2026.
