# Painel de Indicadores Sustentáveis do Brasil — v6

Demo do **Projeto de Bloco: Inteligência Artificial Aplicada** (INFNET) · **Aula 8 · PB Etapa 4**.

Painel ESG/ODS em **Python puro** (sem pandas). Esta versão (**v6**) fecha a **Competência 2**:
o dado passa a **entrar** (CSV enviado pelo usuário) e **sair** (download), o **cache** deixa de ser
invisível — o custo aparece em milissegundos na tela — e as duas memórias do Streamlit ganham
lugares distintos. **Nenhuma dependência nova.**

## Rodar localmente

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows  ·  source .venv/bin/activate no macOS/Linux
pip install -r requirements.txt

python -m src.coleta_web          # 1) COLETA (Aula 7, roda à parte) -> data/processed/
streamlit run app.py              # 2) USO
```

Camadas rodáveis sem interface:

```bash
python -m src.data_access      # coleta as 27 UFs via API (ou usa o cache)
python -m src.transformacoes   # filtra, ordena, resume, compara, exporta CSV
python -m src.noticias         # lê o CSV das notícias e resume a coleta
python -m src.analise_texto    # estatísticas do texto + top de palavras
```

## O que mudou da v5 para a v6

| # | Mudança | Ferramenta | Por quê |
|---|---------|-----------|---------|
| 1 | O usuário **envia o CSV dele** e as linhas entram no painel | `st.file_uploader` | a analista mantém uma planilha à mão |
| 2 | **Validação na borda** — devolve `(linhas, erro)`, nunca levanta exceção | `csv` + `io` | arquivo de fora é **entrada não confiável** |
| 3 | O **envio sobrevive** à troca de filtros | `st.session_state` | sem isso, ele teria de subir o arquivo a cada clique |
| 4 | Cada linha carrega a **procedência** (`coletada` × `enviada`) | — | o *Data Summary Report* do TP2 cobra isso |
| 5 | A base mesclada **sai em CSV** | `st.download_button` | [Raghavendra, p123–124] |
| 6 | O **custo do cache na tela**, com botão para zerar | `@st.cache_data` + `.clear()` | ferramenta invisível não se aprende |
| 7 | **Contagem de palavras** do texto coletado | `collections.Counter` + `st.bar_chart` | a "nuvem de palavras" do enunciado do TP2 |

## Estrutura

```
painel_ods_brasil/
├── app.py                          INTERFACE  — upload, cache medido, palavras
├── src/
│   ├── coleta_web.py               COLETA     — raspa (roda à parte, Aula 7)
│   ├── data_access.py              DADOS      — API do IBGE + fallback
│   ├── noticias.py                 DADOS      — lê o CSV + A BORDA do upload      ← ampliado
│   ├── analise_texto.py            LÓGICA     — contagem de palavras              ← novo
│   └── transformacoes.py           LÓGICA     — filtrar, ordenar, exportar
├── data/processed/                 o que o app lê (VERSIONADO)
├── data/raw/*.html                 snapshots (NÃO versionados)
└── requirements.txt · .gitignore · DEPLOY.md · .streamlit/
```

## As duas memórias — e onde cada uma vive neste app

| | `@st.cache_data` | `st.session_state` |
|---|---|---|
| **Guarda** | o resultado de uma função | o que **este** usuário fez |
| **Indexado por** | os **argumentos** | a **chave** que você escolher |
| **Alcance** | **compartilhado** entre visitantes | **privado** da sessão |
| **Neste app** | `obter_dados()`, `obter_noticias()`, `contar_palavras()` | `favoritas`, `noticias_enviadas` |

**O teste que decide:** *esse valor depende de QUEM está olhando?*
Sim → `session_state`. Não, e é caro → `@st.cache_data`. Nenhum → variável comum.

> ⚠️ **O CSV enviado NUNCA vai para o cache.** O `@st.cache_data` é compartilhado entre visitantes —
> cachear dado de um usuário faria o próximo ver o arquivo do anterior. Não é lentidão: é vazamento.
> O livro é explícito: *"…if that function is called with the same parameters **by another user**…"*
> [Richards, p83].

## O roteiro de demonstração (4 passos)

1. olhe **"Custo NESTE rerun"** e mexa em qualquer filtro → fica em **0 ms**;
2. clique em **Limpar o cache e recoletar** → volta ao custo real;
3. envie `data/processed/noticias.csv` no campo de upload → as linhas entram marcadas como
   **enviada**;
4. **mude o filtro de seções** → o que você enviou **continua lá**. É a *razão de estado* da Aula 6.

## Um comentário no código que NÃO deve ser removido

Em `app.py`, no bloco do upload, há um comentário marcando um defeito real encontrado **no teste**:
a seção nova entrava na lista de opções do `multiselect` e nascia **desmarcada** — o usuário enviava
o arquivo, recebia *"3 acrescentadas"* e **não via nada**. Não quebrava: enganava.

Esse comentário é material didático (o **quebra × engana** da Aula 6, do lado da interface). Ele
fica.

## Publicar

```bash
git add .
git commit -m "v6: upload de CSV, cache medido e nuvem de palavras"
git push
```

O rodapé mostra `v6 — Aula 8 (arquivos, cache e estado de sessão)`.

## Verificação

Confirmado por `AppTest` (Streamlit 1.61), em 02/09/2026:

| Afirmação | Medição |
|---|---|
| O cache economiza a coleta | **677 ms** (1º run) → **1 ms** (reruns seguintes) |
| `st.cache_data.clear()` esvazia | volta a **295 ms** |
| A notícia enviada entra no painel | a seção nova aparece nas **opções** **e fica marcada** |
| O envio sobrevive ao rerun | mexer no filtro não apaga `noticias_enviadas` |
| A borda trata todos os casos | vazio · só cabeçalho · coluna faltando · `latin-1` · válido — sem exceção |
| Duplicata é ignorada | reenviar o mesmo arquivo → *"nada novo"* |
| Contagem de palavras | 10.439 palavras · 5.172 fora as vazias · **2.372** de vocabulário |

## Sobre a nuvem de palavras

Ela é uma **contagem** (`collections.Counter`), desenhada com `st.bar_chart` — barras têm **escala**,
que a nuvem não tem. `wordcloud` + `matplotlib` seriam duas dependências pesadas para um efeito
visual, e o Community Cloud demoraria mais para construir. Quem quiser a nuvem desenhada: instale
**e declare no `requirements.txt`** (regra da Aula 5).

A lista de **palavras vazias** mora visível em `src/analise_texto.py` e **cresceu olhando o
resultado** — a primeira contagem trouxe *pelo, pela, pode, grande*. O que conta como "palavra
vazia" é decisão editorial sua, não da biblioteca.
