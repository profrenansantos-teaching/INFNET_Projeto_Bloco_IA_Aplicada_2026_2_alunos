# Aulas 15–16 (versão compacta) — Material de apoio do aluno
### Quem escolhe, mede; quem pesa, carrega uma vez · PB Etapa 8 · subcompetências 4.3 e 4.4 · **TP4, itens 1 e 2**

> **Este guia é um MAPA.** A Etapa 8 inteira foi dada num encontro só; o material completo continua nos guias das aulas
> separadas — **leia-os**: `../aula-15/student-guide.md` (escolher) e `../aula-16/student-guide.md` (integrar). Aqui
> estão o essencial, a ordem de leitura e o checklist do TP4.
>
> **Antes de tudo — com internet, uma vez:** `pip install -r requirements-api.txt` (no Linux, o `torch` de CPU antes) e
> `python aula-15-16-step-by-step/passo00_baixar.py` (~1,5 GB).

---

## 1. O essencial, em dez linhas

1. **Escolher um modelo é declarar requisitos e medir** — no seu dado, na sua máquina. *"there is not a straightforward
   answer"* [Alto, p81].
2. **A ficha do Hub** (antes de baixar): tarefa, línguas, licença, *gated*, parâmetros × 4 bytes. Ela descarta o
   inacessível; o resto é pista.
3. **Custo é memória e tempo** — e o tipo dos números muda os dois (mDeBERTa: float16 4,5 s × float32 0,57 s).
4. **O banco de provas** (20–30 exemplos rotulados **antes**) é o veredito. Conte os erros **e** os sem resposta.
5. **A justificativa** (TP4, item 1): requisitos, candidatos, medidas, decisão por critério, **o que pesou contra**, limites.
6. **Carregue uma vez**, no `lifespan` — não na rota (a cada pedido, a carga inteira de novo).
7. **A rota do modelo é `def`** — `async def` com o modelo trava a API inteira.
8. **Baixe antes** (`snapshot_download`) e **carregue com `local_files_only=True`**; carga com `try` → **503** se faltar.
9. **Pontue as categorias** do contrato — o modelo deixado escrever devolveu "chuveiro" → 500.
10. **A confiança do modelo não é chance de acerto** — ele errou um relato com 1,00. Diga isso a quem usa.

## 2. Ordem de leitura

| Para… | Leia | E rode |
|-------|------|--------|
| escolher | `../aula-15/student-guide.md` §1–§8 | `aula-15-16-step-by-step/` — os passos da Aula 15 (1 a 5) |
| ver uma justificativa pronta | `../aula-16/demo/painel_ods_brasil/docs/escolha_do_modelo.md` | `python -m src.bancada …` e a página 🧪 |
| integrar | `../aula-16/student-guide.md` §1–§7 | `aula-15-16-step-by-step/` — os passos da Aula 16 (1 a 5), com `cronometro.py` |
| ver tudo junto | `../aula-16/demo/painel_ods_brasil/README.md` | `python -m src.baixar_modelo` · `uvicorn api.main:app` · `streamlit run app.py` |

## 3. Os números que você vai encontrar (todos medidos)

| Escolher (bancada, 30 relatos) | | Integrar (`uvicorn` real) | |
|---|---|---|---|
| regras | 13 (17 sem resposta) | carga a cada pedido (0.5B) | 6,1 · 2,1 · 2,1 s |
| BART (o mais baixado) | 9 | no `lifespan` | 0,4 s por pedido |
| mDeBERTa | 18 — 4,5 s (fp16) × 0,57 s (fp32) | `/saude` com `async def` × `def` | 1,64 s × 0,00 s |
| Qwen2.5-0.5B | 4 → 11 (com definições) | sem o modelo: pelo nome × `local_files_only` | 82,5 s (sem internet) × 0,4 s |
| **Qwen2.5-1.5B** | **27** — 2,8 s, 6,2 GB (fp32) | a v14 (1.5B): subida · uma análise | ~21 s · ~2,5 s |

## 4. O checklist do TP4

| # | O TP4 pede | Onde ver como se faz |
|--:|------------|----------------------|
| 1 | a escolha do modelo, justificada (desempenho, custo, acessibilidade) | `docs/escolha_do_modelo.md` (v14) · `../aula-15/student-guide.md` §8 |
| 2 | o modelo do Hugging Face, local, atrás de `POST /processar_texto` | `src/analisador_llm.py` · `src/baixar_modelo.py` · `api/main.py` (`lifespan`) |
| 3 | response models; respostas validadas | `api/respostas.py` — a categoria sempre da lista (pontuar) |
| 4 | 503 do modelo; entrada (422); timeout; feedback útil | `api/rotas/analise.py` · `src/cliente_api.py` · `paginas/analisador.py` |
| — | o README: a memória e o tempo que o modelo pede; como baixá-lo | `README.md` da v14 |

Entrega: semana de **16–21/11/2026** — `nome_sobrenome_PB_TP4.PDF`, com o link do repositório.

## 5. Fontes

ALTO, V. *Building LLM Powered Applications* (Packt, 2024), cap. 3 [K3] · PARANDEH, A. *Building Generative AI Services
with FastAPI* (O'Reilly, 2025), caps. 3 e 5 [H3] · documentação do Hugging Face, do Transformers e do FastAPI. Os livros
não tratam de CPU, português, modo offline nem de encaixar o modelo num contrato — os guias completos explicam o que foi
medido no lugar.
