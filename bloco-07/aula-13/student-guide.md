# Aula 13 — Material de apoio do aluno
### Quem responde, promete · PB Etapa 7 · subcompetência 4.1 · **TP4, itens 2 e 3**

> Consulte enquanto faz o TP4: a rota que **recebe um texto e devolve a análise** (*"POST /processar_texto"*,
> item 2), com uma resposta **estruturada e validada** — *"o texto processado, o tipo de análise realizada… e os
> resultados gerados"* (item 3). O que esta aula cobre — e o que vem na Aula 14 e na Etapa 8 — está na seção 8.

---

## 1. Uma resposta tem três partes

*"A response consists of a header and a body."* [Adeshina, p61] — e um **status**:

| Parte | O que é | Exemplo |
|-------|---------|---------|
| **status** | um número de três dígitos; *"The first digit of a status code defines its category"* [p62] | `200`, `201`, `422`, `500` |
| **cabeçalho** | informações para ler o corpo | `content-type: application/json` |
| **corpo** | o dado | `{"tipo_analise": "classificacao", …}` |

| Família | Quer dizer [Adeshina, p61] |
|---------|----------------------------|
| **2xx** | *"The request was successful."* |
| **4xx** | *"There's an error from the client."* |
| **5xx** | *"There's an error from the server."* |

---

## 2. Sem modelo de resposta, a API não diz o que devolve

```python
@app.post("/processar_texto")
def processar_texto(pedido: PedidoAnalise):
    return classificar(pedido.texto)        # devolve o que a função montou — tudo
```

No `/docs`, a resposta 200 aparece como **`"string"`**. Quem vai usar a sua API (outro programa, o seu painel, o
avaliador do TP4) tem de **adivinhar** os campos. E recebe tudo o que a função calculou — inclusive detalhes
internos que ninguém deveria usar.

---

## 3. O modelo de resposta: filtra, confere, documenta

*"Response models serve as templates for returning data from an API route path."* [Adeshina, p60]

```python
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class ResultadoAnalise(BaseModel):
    model_config = ConfigDict(json_schema_extra={"examples": [{
        "tipo_analise": "classificacao", "texto": "O nível do rio baixou…", "categoria_sugerida": "seca",
        "confianca": 1.0, "pistas": ["nível do rio", "baixou"], "motor": "regras-v1"}]})
    tipo_analise: Literal["classificacao"]
    texto: str
    categoria_sugerida: Literal["queimada", "seca", "enchente", …] | None    # None: não achou
    confianca: float = Field(ge=0, le=1)
    pistas: list[str]
    motor: str

@app.post("/processar_texto", response_model=ResultadoAnalise)
def processar_texto(pedido: PedidoAnalise):
    return {"tipo_analise": pedido.tipo_analise, "texto": pedido.texto, **analisar(pedido.texto)}
```

| O `response_model`… | Na prática |
|---------------------|-----------|
| **filtra** | só os campos do modelo saem. O que a função calculou a mais **fica no servidor** |
| **confere** | o que a função devolve passa pelo modelo. `"431"` vira `431` se o modelo diz `int`; o que não dá para converter → **500** (seção 4) |
| **documenta** | o `/docs` mostra os campos (e o exemplo); os *Schemas* ficam no fim da página |

**Dois jeitos de declarar** — o mesmo efeito:

```python
@app.get("/relatos", response_model=list[RelatoGravado])     # o do livro [Adeshina, p64]
def relatos(): ...

@app.get("/relatos")
def relatos() -> list[RelatoGravado]: ...                     # a anotação de retorno
```

> ⚠️ **Livro × hoje.** O livro escreve `-> dict` **e** `response_model=` [p64] — havendo os dois, vale o
> `response_model`. Usa `typing.List` [p63] — hoje, `list[...]`. E configura o exemplo com `class Config:
> schema_extra` [p63–64] — no Pydantic 2, o exemplo **some** do `/docs`: use `model_config =
> ConfigDict(json_schema_extra=…)` (Aula 12).

> **IA como copiloto.** Peça a uma IA o modelo de resposta da sua rota, mostrando um exemplo do que a função
> devolve. Ela tende a copiar **todos** os campos do exemplo — inclusive os que você não quer prometer — e pode
> declarar `datetime` para qualquer coisa que pareça data. **Cada campo do contrato é uma promessa sua.** Confira
> com a seção 4.

---

## 4. 🐛 Quando a API quebra a própria promessa: 500

| O modelo diz… | O dado é… | Resposta |
|---------------|-----------|:--------:|
| `Relato` (o modelo de **entrada**, com `extra="forbid"`) | o relato **gravado**, com `id` e `recebido_em` | **500** |
| `publicado_em: datetime` | `"02/09/2026 08:16"` | **500** |

O cliente recebe *"Internal Server Error"*, em texto puro. **O motivo está no terminal do `uvicorn`:**

```
fastapi.exceptions.ResponseValidationError: 6 validation errors:
  {'type': 'extra_forbidden', 'loc': ('response', 0, 'id'), 'msg': 'Extra inputs are not permitted', …}
```

| | 422 (Aula 12) | 500 (hoje) |
|---|---|---|
| quem errou | **o cliente** mandou errado | **a API** respondeu errado |
| `loc` começa com | `"body"`, `"query"`, `"path"` | `"response"` |
| o cliente lê o motivo? | sim, no `detail` | **não** — está no terminal |

**Duas regras:**
- **Um contrato para cada direção.** O que entra (`Relato`) não é o que sai (`RelatoGravado`): a saída tem o que a
  API acrescentou.
- **Prometa só o que o seu dado cumpre.** Se a data está gravada como `dd/mm/aaaa hh:mm`, declare `str` (e diga o
  formato na `description`) — ou converta para ISO **antes** e declare `datetime`. Não prometa um tipo que o dado
  não tem.

---

## 5. 200 ou 201?

*"It is also important to note that the default status code for success is 200."* [Adeshina, p68]

```python
from fastapi import status

@router.post("", status_code=status.HTTP_201_CREATED, response_model=RelatoRecebido)   # criou algo: 201
```

| Rota | Status |
|------|:------:|
| consulta (`GET`) · análise (`POST /processar_texto` — não cria nada) | **200** |
| envio que **grava** algo novo (`POST /relatos`) | **201** |

⚠️ **Mudar o status é mudar o contrato.** Um cliente que confere `r.status_code == 200` passa a dizer "falhou" a
um 201. **No cliente, confira a família:**

```python
if r.ok:                        # 2xx — 200, 201… (r.ok é verdadeiro para tudo abaixo de 400)
    ...
```

---

## 6. A rota do TP4: o contrato antes do motor

```
o painel / a prefeitura  ──►  PedidoAnalise  ──►  o MOTOR  ──►  ResultadoAnalise  ──►  o painel / a prefeitura
                              (o que entra)      (troca!)       (o que sai)
```

| Campo | O TP4 (item 3) pede |
|-------|---------------------|
| `texto` | *"o texto processado"* |
| `tipo_analise` | *"o tipo de análise realizada (resumo, classificação, etc.)"* |
| o resultado (`categoria_sugerida`, `confianca`, `pistas` — ou `resumo`, `sentimento`…) | *"os resultados gerados"* |
| `motor` | quem analisou (útil para o diagnóstico) |

**Escreva o contrato antes de escolher o LLM.** Use um motor simples (regras, contagem de palavras) para pôr a rota
de pé. Na Etapa 8, troque **só** a função do motor: a rota e os dois modelos ficam, e quem usa a rota não muda nada.

**O que NÃO prometer:** o que só o motor de hoje calcula. O nosso motor de regras conta as pistas de **todas** as
categorias — um LLM não teria essas contagens. Se estivessem no contrato, a Etapa 8 quebraria quem as usa.

> **E o caso vazio?** O motor pode não achar nada (*"a água do arroio subiu"* não tem nenhuma palavra da nossa
> lista). O contrato precisa caber esse caso: `categoria_sugerida: … | None`, `pistas: list[str]` (vazia). Sem o
> `| None`, o primeiro texto que o motor não entende vira **500**.

---

## 7. Anti-padrões desta aula

| Anti-padrão | Por que dói |
|-------------|-------------|
| rota sem modelo de resposta | o `/docs` diz `"string"`; o cliente adivinha |
| devolver tudo o que a função calcula | detalhes internos viram contrato sem querer |
| reusar o modelo de **entrada** na saída | `forbid` + os campos que a API acrescenta = **500** |
| prometer um tipo que o dado não cumpre (`datetime` para `dd/mm/aaaa`) | **500** na rota inteira |
| esquecer o caso vazio (`str` sem `\| None`) | **500** no primeiro texto que o motor não entende |
| conferir `== 200` no cliente | um 201 vira "falhou" |
| copiar `class Config: schema_extra` do livro | roda, avisa — e o exemplo some |

---

## 8. O TP4, depois desta aula

**O que esta aula cobre:**

- [ ] **Item 2:** a rota `POST /processar_texto` de pé — o pedido validado (Aula 12) e um motor (provisório, por
      enquanto)
- [ ] **Item 3:** `response_model` na rota — o texto processado, o tipo de análise e os resultados, com tipos
- [ ] **Item 3:** *"todos os retornos da API validados"* — um modelo de resposta em **cada** rota; nenhum
      `"string"` no `/docs`
- [ ] o status certo nos envios que gravam (**201**), e o cliente conferindo a família
- [ ] o painel (ou outro cliente) lendo **só** os campos do contrato

**O que vem:**

- [ ] **Aula 14 — item 4:** exceções HTTP (404, 503…) e mensagens úteis para o usuário
- [ ] **Etapa 8 — itens 1 e 2:** o **modelo LLM local**, escolhido por desempenho, custo e acessibilidade — no
      lugar do motor provisório, **no mesmo contrato**
- [ ] **Entrega:** `nome_sobrenome_PB_TP4.PDF` com o **link do repositório no GitHub** (calendário: semana de
      16–21/11)

---

## 9. Fontes

- **ADESHINA, A. A.** *Building Python Web APIs with FastAPI*. Packt, 2022 — cap. 3 (*Response Models and Error
  Handling*: resposta, cabeçalho e corpo, p61; famílias de status, p61–62; *response models*, p60–65;
  `status_code=201`, p68). **[G3]** — páginas do PDF.
- Documentação oficial do FastAPI e do Pydantic 2 — *Response Model*, anotação de retorno, `ResponseValidationError`.
  Verificados por execução (FastAPI 0.142, Pydantic 2.13, uvicorn 0.52, Streamlit 1.61), em 27/10/2026.
