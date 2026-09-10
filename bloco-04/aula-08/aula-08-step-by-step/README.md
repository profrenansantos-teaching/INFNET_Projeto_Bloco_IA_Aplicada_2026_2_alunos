# Aula 8 — Passo a passo: o arquivo entra, o arquivo sai

> Cada passo é um app Streamlit **completo e independente**. Rode, mexa, entenda — só então vá ao
> próximo. O destino é a **v6** em `../demo/painel_ods_brasil/`. **Nenhum passo precisa de internet.**

```bash
streamlit run passo01_upload.py
```

| Passo | Arquivo | O que ensina | Subcomp. |
|------:|---------|--------------|----------|
| **1** | `passo01_upload.py` | `st.file_uploader`: devolve `None`, depois devolve o mesmo arquivo **em todo rerun** | 2.3 |
| **2** | `passo02_validar_na_borda.py` | validar na borda: vazio, codificação, colunas faltando — **devolver erro, não levantar** | 2.3 |
| **3** | `passo03_cache.py` | `@st.cache_data` com o **custo na tela**; `ttl`; `.clear()`; `cache_data` × `cache_resource` | 2.5 |
| **4** | `passo04_cache_x_estado.py` | as duas memórias lado a lado — e os **dois erros simétricos** | 2.5 |
| **5** | `../demo/painel_ods_brasil/app.py` | tudo junto, no Painel ODS — a **v6** | 2.3 + 2.5 |

---

## A ideia que amarra os quatro passos

O Streamlit tem **duas memórias**, e elas respondem a perguntas diferentes:

| | `@st.cache_data` | `st.session_state` |
|---|---|---|
| **Guarda** | o resultado de uma função | o que este usuário fez |
| **Indexado por** | os **argumentos** da chamada | a **chave** que você escolher |
| **Alcance** | **compartilhado** entre visitantes | **privado** da sessão |
| **Dura** | até o `ttl` vencer ou `.clear()` | a sessão (F5 começa outra) |
| **Serve para** | não repetir trabalho **caro** | **atravessar** reruns |

**O teste que decide:** *esse valor depende de QUEM está olhando?*
Se sim → `session_state`. Se não, e é caro → `@st.cache_data`. Se nenhum dos dois → variável comum.

> É a mesma disciplina da **razão de estado** da Aula 6: memória se pede quando se precisa, e se
> justifica.

## Os dois erros simétricos (o motivo de existir o passo 4)

| Erro | O que acontece |
|------|----------------|
| Guardar a coleta do IBGE em `session_state` | cada visitante paga a chamada de rede de novo |
| Cachear o CSV que o usuário enviou | o próximo visitante vê o arquivo do anterior — **vazamento** |

## Números medidos (não estimados)

| Onde | Medição |
|------|---------|
| `passo03_cache.py` | primeira chamada **≈ 1.200 ms**; com cache, **0 ms**; depois de `.clear()`, **1.202 ms** |
| `demo/` (v6, coleta do IBGE) | primeira **677 ms**; nos reruns seguintes, **1 ms** |

Verificado com `AppTest` (Streamlit 1.61) em 02/09/2026.

## Depois dos quatro passos

```bash
cd ../demo/painel_ods_brasil
python -m src.coleta_web        # (Aula 7) gera data/processed/ — se ainda não fez
streamlit run app.py
```

No app v6, faça o roteiro:

1. olhe **"Custo NESTE rerun"** e mexa num filtro → fica em **0 ms**;
2. clique em **Limpar o cache** → volta ao custo real;
3. envie `data/processed/noticias.csv` no campo de upload → as linhas entram marcadas
   como *enviada*;
4. **mude o filtro de seções** → o que você enviou **continua lá**. Essa é a razão de estado.
