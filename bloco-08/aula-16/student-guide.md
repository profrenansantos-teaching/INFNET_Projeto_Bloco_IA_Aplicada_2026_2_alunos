# Aula 16 — Material de apoio do aluno
### Quem pesa, carrega uma vez · PB Etapa 8 · subcompetência 4.4 · **TP4, item 2** (e o fecho dos itens 3 e 4)

> **O que você leva desta aula:** como pôr o modelo que você escolheu **atrás da rota do TP4** — sem que cada pedido
> pague a carga, sem travar a API, sem depender de internet, e dentro do contrato. Os passos estão em
> `../aula-15-16/aula-15-16-step-by-step/`; o projeto completo, na v14 (`demo/painel_ods_brasil/`).

---

## 1. O modelo é a peça mais pesada que a sua API já teve

| O peso | No demo (Qwen2.5-1.5B, CPU) | A decisão |
|--------|-----------------------------|-----------|
| carregar | ~9 s, ~6,5 GB de memória | **uma vez**, quando a API sobe (§2) |
| pensar | ~2,5 s por relato; 8,1 s com 2.000 caracteres | a rota é **`def`** (§3) |
| os arquivos | 3,1 GB que podem não estar no disco | **baixar à parte**; carregar com `local_files_only`; **503** (§4) |
| o que ele responde | um texto qualquer — "chuveiro" | **pontuar** as categorias do contrato (§5) |

## 2. Carregar uma vez: o `lifespan`

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

MOTORES = {}                                   # o modelo carregado mora aqui

@asynccontextmanager
async def lifespan(_: FastAPI):
    MOTORES["analise"] = carregar_motor()      # ANTES do yield: quando a API sobe
    yield
    MOTORES.clear()                            # DEPOIS do yield: quando a API desce

app = FastAPI(lifespan=lifespan)

@app.post("/processar_texto")
def processar_texto(pedido: PedidoAnalise):
    return classificar_com_modelo(pedido.texto, MOTORES["analise"])   # a rota só USA
```

> *"The most compute-efficient strategy for loading models in FastAPI is to use the application lifespan."*
> [Parandeh, p128]

**Medido (passos 1–2, com o modelo pequeno):** carregando na rota, **6,1 · 2,1 · 2,1 s** por pedido; no `lifespan`,
**0,4 s** — e a carga (3,7 s) uma vez só, antes de *Application startup complete*.

- `@app.on_event("startup")` é a forma **antiga** — o livro a chama de *legacy* [p130]. Use o `lifespan`.
- **Testes:** o `TestClient` só roda o `lifespan` dentro de `with TestClient(app) as c:` (fora dele, o modelo não
  carrega — verificado).

## 3. A rota do modelo é `def` — não `async def`

| Como a rota é declarada | Onde o FastAPI a roda | Enquanto o modelo pensa… |
|-------------------------|-----------------------|--------------------------|
| `async def` | no **laço principal** — o mesmo que atende **todos** os pedidos | **todas** as rotas esperam (o `/saude` esperou **1,64 s**) |
| `def` | numa **thread à parte** | as outras rotas seguem (o `/saude`: **0,00 s**) |

> *"when you declare handlers with async def, FastAPI trusts you with performing only nonblocking operations. When you
> break that trust… the event loop will be blocked"* [Parandeh, p192]

`async def` é para quem **espera** algo de fora, com `await` (uma chamada de rede). O modelo local **calcula** — não há
`await` ali. **Regra: a rota que chama o modelo local é `def`.** (O próprio livro escorrega nos exemplos 5-7 e 5-14.)

**E dois pedidos ao mesmo tempo?** Rodam — e **dividem a CPU**: 4,6 s cada (sozinho, ~2,5 s).

## 4. O modelo mora no disco: baixe antes, leia offline, e falhe em pedaços

**O download é um passo à parte** (como a coleta das Aulas 7 e 10):

```python
from huggingface_hub import snapshot_download
snapshot_download("Qwen/Qwen2.5-1.5B-Instruct",
                  allow_patterns=["*.json", "*.safetensors", "*.txt", "tokenizer*", "merges.txt", "vocab.*"])
```

**A API só lê do disco:**

```python
tokenizador = AutoTokenizer.from_pretrained(MODELO, local_files_only=True)
modelo = AutoModelForCausalLM.from_pretrained(MODELO, local_files_only=True, dtype=torch.float32)
```

| Sem o modelo no disco | Carregando pelo nome | Com `local_files_only=True` |
|-----------------------|----------------------|-----------------------------|
| **com** internet | a **subida** baixa 3,1 GB — **71 s** sem responder a nada | `OSError` em **0,4 s** |
| **sem** internet | 5 tentativas: `OSError` depois de **82,5 s** | `OSError` em **0,4 s** |

**E a carga tem `try`** — senão, uma exceção no `lifespan` derruba a subida inteira (*Application startup failed.
Exiting.*):

```python
def carregar_na_subida():
    try:
        MOTORES["analise"] = carregar_motor()
    except Exception as falha:        # a fronteira: qualquer falha na carga vira 503
        log.error("Modelo NÃO carregado — %s: %s", type(falha).__name__, falha)

@app.post("/processar_texto")
def processar_texto(pedido: PedidoAnalise):
    if "analise" not in MOTORES:
        raise HTTPException(503, detail="O analisador de texto está indisponível: o modelo de linguagem não foi "
                                        "carregado quando a API subiu. As outras rotas funcionam normalmente.")
    ...
```

É o 503 do TP4 (item 4) — e o "falhe em pedaços" da Aula 14.

## 5. O modelo cabe no contrato — não o contrário

Deixado **escrever**, um LLM escreve o que quiser. O modelo pequeno escreveu **"chuveiro"**; o `response_model` (as seis
categorias) conferiu e a rota respondeu **500** (`ResponseValidationError … 'input': 'chuveiro'`). E a confiança? Um
texto não traz número.

**Pontuar as categorias:** o modelo lê as instruções e o relato, e olhamos **uma vez** a próxima palavra que ele diria —
só as seis categorias:

```python
entrada = tokenizador.apply_chat_template(mensagens, add_generation_prompt=True, return_tensors="pt", return_dict=True)
with torch.no_grad():
    notas = modelo(**entrada).logits[0, -1, tokens_das_categorias]   # o 1º token de cada categoria
probabilidades = torch.softmax(notas, dim=0)                          # somam 1
```

| | Escrever | Pontuar |
|---|---|---|
| a resposta | qualquer texto | **sempre** uma das seis |
| a confiança | não existe | a probabilidade |
| no banco de provas (1.5B) | 27 de 30 · 2,8 s | 27 de 30 · **2,2 s** |

**Exemplo real** (relato nº 7, *"o céu ficou alaranjado… fuligem preta"*): queimada **0,81** · poluição 0,12 · enchente
0,07.

## 6. A confiança do modelo não é chance de acerto

O modelo errou o relato nº 2 (*"o nível do rio baixou tanto que o barco não chega ao porto"* — seca; ele disse enchente)
com **confiança 1,00**. Dos 27 acertos, 25 vieram com ≥ 0,94 — e os três erros, com 1,00, 0,81 e 0,96. **Diga isso a quem
usa:** a v14 mostra, abaixo da resposta, que quem analisou foi um modelo de linguagem e que a confiança é uma **aposta**.

## 7. O contrato não mudou — o que os campos dizem, sim

| Campo de `ResultadoAnalise` | Com as regras (v11–v13) | Com o modelo (v14) |
|-----------------------------|-------------------------|--------------------|
| `categoria_sugerida` | uma das seis ou `null` | **sempre** uma das seis |
| `confianca` | a fração das pistas | a probabilidade do modelo |
| `pistas` | as palavras encontradas | `[]` |
| `motor` | `regras-v1 (palavras-chave)` | `Qwen/Qwen2.5-1.5B-Instruct` |

O painel não mudou **a chamada**; mudou **o que a página diz**: a espera, a ausência de pistas, o aviso da confiança.

## 8. Anti-padrões desta aula

| Anti-padrão | O que acontece (medido) |
|-------------|-------------------------|
| carregar o modelo **na rota** | cada pedido paga a carga (~9 s com o 1.5B) |
| **`async def`** com a inferência | a API inteira espera o modelo pensar |
| carregar **sem `try`** | *Application startup failed* — a API toda fora |
| **baixar na subida** | 71 s muda; sem internet, 82,5 s até falhar |
| devolver o **texto cru** do modelo | "chuveiro" → 500 |
| **inventar** uma confiança | um número que o usuário leva a sério |
| esconder que é **um modelo, e que erra** | o usuário confia num erro de 100% |
| `--reload` com o modelo, só para usar o painel | cada `.py` salvo recarrega o modelo |

## 9. O TP4 completo

| Item | Onde, na v14 |
|------|--------------|
| 1 — a escolha e a justificativa | `docs/escolha_do_modelo.md` (Aula 15) |
| 2 — o modelo local atrás de `POST /processar_texto` | `src/analisador_llm.py` · `src/baixar_modelo.py` · `api/main.py` (`lifespan`) · `api/rotas/analise.py` |
| 3 — response models, respostas validadas | `api/respostas.py` (Aula 13) — a categoria sempre da lista |
| 4 — erros: o 503 do modelo, os dados de entrada, o timeout; feedback útil | `api/rotas/analise.py` · `api/erros.py` · `src/cliente_api.py` · `paginas/analisador.py` |

**No README do seu projeto:** quanto de memória e de tempo o modelo pede, e como baixá-lo. Entrega: semana de
**16–21/11/2026** — `nome_sobrenome_PB_TP4.PDF`, com o link do repositório.

## 10. Fontes

- PARANDEH, A. *Building Generative AI Services with FastAPI*. O'Reilly, 2025 — cap. 3 (*AI Integration and Model
  Serving*: Ex. 3-1, 3-2, 3-16, 3-17); cap. 5 (concorrência: p187–192). [H3]
- Documentação: FastAPI (*Lifespan Events*, *Concurrency and async/await*); Transformers (`from_pretrained`,
  `local_files_only`, `dtype`); `huggingface_hub` (`snapshot_download`).
- **O livro recomenda GPU** e roda o modelo por `pipeline`, deixando-o escrever; não trata de modo offline, de 503 para
  o modelo nem de encaixar a saída num contrato. Esta aula preenche essas lacunas — tudo medido numa CPU comum.
