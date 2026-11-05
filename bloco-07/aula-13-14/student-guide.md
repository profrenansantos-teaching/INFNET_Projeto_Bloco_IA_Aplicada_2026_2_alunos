# Aulas 13–14 — Material de apoio do aluno
### Quem responde, promete; quem falha, explica · PB Etapa 7 · subcompetências 4.1 e 4.2 · **TP4, itens 2, 3 e 4**

> A Etapa 7 coube num encontro só. Este guia é o **mapa** do que vimos, na ordem da aula, com o caminho para os guias
> completos de cada metade — **leia-os enquanto faz o TP4**:
> - **`../aula-13/student-guide.md`** — o contrato da **resposta** (*response models*), a rota do TP4
> - **`../aula-14/student-guide.md`** — o contrato do **erro** (exceções HTTP), o cliente que lê pelo status

---

## 1. Quem responde, promete — o contrato do que sai

| Ideia | Em uma linha | No guia |
|-------|--------------|---------|
| uma resposta tem status, cabeçalho e corpo | *"The first digit of a status code defines its category."* [Adeshina, p62] | 13 §1 |
| sem `response_model`, o `/docs` diz `"string"` | e o cliente adivinha os campos | 13 §2 |
| `response_model` **filtra, confere, documenta** | só sai o que está no modelo; o que não cumpre vira 500 | 13 §3 |
| **um contrato para cada direção** | o modelo de entrada (com `forbid`) na resposta → **500** | 13 §4 |
| **prometa só o que o dado cumpre** | `datetime` para `"02/09/2026 08:16"` → **500** | 13 §4 |
| 200 × **201** | criou algo: 201 — e, no cliente, confira a família (`r.ok`) | 13 §5 |

```python
@app.post("/processar_texto", response_model=ResultadoAnalise)    # o que SAI: os campos do contrato
def processar_texto(pedido: PedidoAnalise): ...                    # o que ENTRA: o modelo da Aula 12
```

## 2. O contrato antes do motor — a rota do TP4

`ResultadoAnalise`: `texto` (*"o texto processado"*), `tipo_analise` (*"o tipo de análise realizada"*), o resultado
(`categoria_sugerida` ou `null`, `confianca`, `pistas`) e `motor`. **Escreva o contrato antes de escolher o LLM**; na
Etapa 8, troque só a função do motor. E não prometa o que só o motor de hoje calcula. → **13 §6**

## 3. Quem falha, explica — o contrato do erro

| Status | Quando | `detail` | No guia |
|:------:|--------|----------|---------|
| **422** | o pedido não cumpre o contrato | uma **lista** | 14 §1 |
| **404** | o que se pediu **não existe** (o caminho identifica) — o filtro vazio é **200 `[]`** | uma frase | 14 §2 |
| **409** | o pedido conflita com o que já existe (o mesmo relato) | uma frase | 14 §2 |
| **503** | falta algo no servidor — **o modelo não carregou** (TP4) | uma frase | 14 §4 |
| **500** | o imprevisto — com a rede de segurança: JSON + um código no log | uma frase com o código | 14 §5 |

```python
raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail="O PRODES não tem a taxa de 2026: a série vai de 1988 a 2025.")
```

**Falhe em pedaços:** carregue o modelo com `try` — se falhar, a API sobe e só a rota dele responde 503. **Ao usuário, a
frase; ao log, o traceback.** E declare os erros no `/docs` (`responses=`). → **14 §3–5**

## 4. Do outro lado: o cliente que lê pelo status

O `detail` do 422 é uma lista; o dos outros, uma frase — **o status decide como ler o corpo**. Sem resposta:
`ConnectionError` (*"não está no ar"*) × `ReadTimeout` (*"demorou"* — um LLM na CPU). E o tom: 409 e 503 são avisos;
422 e 500, erros. → **14 §6**

## 5. O TP4, depois desta aula — a Etapa 7 completa

- [ ] **Item 2:** `POST /processar_texto` de pé, com o pedido validado
- [ ] **Item 3:** `response_model` na rota — o texto, o tipo de análise, o resultado — e um modelo de resposta em
      **toda** rota (*"todos os retornos… validados"*)
- [ ] **Item 4:** `HTTPException` com o status certo (404, 409, **503 do modelo**); `detail` claro; o 500 com código
- [ ] **Item 4:** o painel lendo pelo status, com *"feedback útil para o usuário final"*
- [ ] os erros **declarados** no `/docs`
- [ ] **Etapa 8 (itens 1 e 2):** o modelo LLM local no lugar do motor provisório — no mesmo contrato
- [ ] **Entrega:** `nome_sobrenome_PB_TP4.PDF` com o link do repositório (calendário: semana de 16–21/11)

## 6. Onde está o código

| O quê | Onde |
|-------|------|
| o demo ao fim da aula (**v12**) | `../aula-14/demo/painel_ods_brasil/` |
| o demo da metade "respostas" (**v11**) | `../aula-13/demo/painel_ods_brasil/` |
| os passos vistos em aula | `aula-13-14-step-by-step/` — Aula 13: passos 1, 2, 3, 5 · Aula 14: passos 1, 3, 4 (o `README.md` da pasta segue a ordem da aula) |
| os passos que ficaram para casa | 13: passo 4 (o cliente `== 200`) · 14: passo 2 (409 e `responses=`) e passo 5 (o cliente que lê pelo status) |

## 7. Fontes

- **ADESHINA, A. A.** *Building Python Web APIs with FastAPI*. Packt, 2022 — **cap. 3** inteiro (*Response Models and
  Error Handling*, p60–69). **[G3]** — páginas do PDF.
- Documentação oficial do FastAPI, do Pydantic 2 e do `requests`. Verificados por execução em 27/10/2026.
