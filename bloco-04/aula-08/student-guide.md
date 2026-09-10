# Aula 8 — Material de apoio do aluno
### O arquivo entra, o arquivo sai · PB Etapa 4 · subcompetências 2.3 e 2.5

> Consulte enquanto fecha o **TP2**. O checklist da seção 8 é o mesmo que o professor percorre no
> fim da aula.

---

## 1. Upload: `st.file_uploader`

```python
enviado = st.file_uploader("Escolha um arquivo CSV", type="csv")

if enviado is None:
    st.info("Envie um CSV para acrescentar dados ao painel.")
else:
    bruto = enviado.getvalue()      # BYTES, não texto
```

### Três coisas que surpreendem

| O quê | Por quê | O que fazer |
|-------|---------|-------------|
| Devolve **`None`** antes de qualquer envio | não há evento; é um widget como qualquer outro | proteja tudo com `if enviado is None: ... else: ...` |
| `getvalue()` devolve **bytes** | o arquivo veio de fora; ninguém garantiu a codificação | decodifique **você**, na borda (seção 2) |
| Devolve o **mesmo arquivo em todo rerun** | o script roda inteiro a cada interação (Aula 6) | **nunca** empilhe sem checar duplicata |

### 🐛 O erro que todo mundo comete uma vez

```python
# ERRADO — a lista cresce a cada clique em QUALQUER widget do app
st.session_state.enviadas.extend(linhas)

# CERTO — a mesma solução do comparador da Aula 6
ja_tenho = {x["url"] for x in st.session_state.enviadas}
novas = [linha for linha in linhas if linha["url"] not in ja_tenho]
st.session_state.enviadas.extend(novas)
```

`type="csv"` filtra pela **extensão**, e só. Um `.xlsx` renomeado passa.

---

## 2. Validar na borda

Arquivo que vem de fora é **entrada não confiável**. Uma função só, na entrada, que **devolve** o
erro em vez de levantá-lo:

```python
COLUNAS_OBRIGATORIAS = ("secao", "titulo", "url")

def ler_csv_enviado(conteudo: bytes) -> tuple[list[dict], str]:
    """Devolve (linhas, mensagem_de_erro). Nunca levanta exceção."""
    if not conteudo:
        return [], "O arquivo está vazio."

    texto = None
    for codificacao in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            texto = conteudo.decode(codificacao)
            break
        except UnicodeDecodeError:
            continue
    if texto is None:
        return [], "Não consegui ler o arquivo como texto. Ele é mesmo um CSV?"

    linhas = list(csv.DictReader(io.StringIO(texto)))
    if not linhas:
        return [], "O CSV não tem nenhuma linha de dados (só o cabeçalho, talvez)."

    faltando = [c for c in COLUNAS_OBRIGATORIAS if c not in linhas[0]]
    if faltando:
        return [], "Faltam colunas obrigatórias: " + ", ".join(faltando) + "."

    return linhas, ""
```

### Por que essa ordem de codificações

| Ordem | Codificação | Motivo |
|:-----:|-------------|--------|
| 1ª | `utf-8-sig` | é o que o **Excel** gera: UTF-8 **com BOM**. Sem isso, a primeira coluna vira `'﻿secao'` e a checagem de colunas falha — sem erro nenhum |
| 2ª | `utf-8` | o padrão de todo o resto |
| 3ª | `latin-1` | **sempre por último**: `latin-1` **nunca falha** (decodifica qualquer byte). Se viesse antes, aceitaria lixo em silêncio |

### Três regras da borda

1. **Devolva o erro, não o levante.** Erro de arquivo do usuário é **rotina**, não exceção.
2. **A mensagem diz o que fazer.** *"Faltam colunas obrigatórias: url"* é acionável;
   *"arquivo inválido"* não é.
3. **Valide ANTES de guardar.** Depois da borda, o resto do app não precisa desconfiar de nada.

---

## 3. Download: `st.download_button`

```python
st.download_button(
    "⬇ Baixar CSV",
    data=para_csv(recorte),          # str ou bytes, já em memória
    file_name="noticias_painel.csv",
    mime="text/csv",
)
```

[Raghavendra, p123–124]

- **Baixe o recorte que está na tela**, não a base inteira: o usuário leva o que ele vê.
- **Marque a procedência** de cada linha (`coletada` × `enviada`). Dado sem procedência é dado que
  ninguém consegue auditar — e é o que o **Data Summary Report** do TP2 cobra.

---

## 4. Cache: `@st.cache_data`

```python
@st.cache_data(ttl=3600, show_spinner=False)
def obter_dados():
    inicio = time.perf_counter()
    dados, fonte = carregar_dados()
    return dados, fonte, time.perf_counter() - inicio    # o custo viaja junto

relogio = time.perf_counter()
dados, fonte, custo_original = obter_dados()
custo_agora = time.perf_counter() - relogio              # ~0 se o cache respondeu
```

**Medido no demo** (`AppTest`, Streamlit 1.61):

| Situação | Custo neste rerun |
|---|---|
| Primeira execução | **677 ms** |
| Reruns seguintes | **1 ms** |
| Depois de `st.cache_data.clear()` | **295 ms** |

### O que invalida o cache

Os **parâmetros de entrada**, o valor de **variáveis externas** usadas na função, o **corpo** da
função e o corpo das funções chamadas dentro dela. [Raghavendra, p185]

```python
st.cache_data.clear()    # esvazia TODOS os @st.cache_data do app
st.rerun()               # era st.experimental_rerun() nas versões antigas
```

### `cache_data` × `cache_resource`

| | `@st.cache_data` | `@st.cache_resource` |
|---|---|---|
| Para que | **dados** (listas, dicionários, JSON) | **conexões e modelos** |
| O que guarda | uma **cópia** do resultado | o **próprio objeto**, compartilhado |
| No curso | coleta do IBGE, leitura de CSV, contagem de palavras | (ainda não usamos) |

> "There are two Streamlit caching functions, one for data (`st.cache_data`) and one for resources
> like database connections or machine learning models (`st.cache_resource`)." [Richards, p83]

### ⚠️ APIs que envelheceram

| No livro (2023) | Hoje (Streamlit ≥ 1.40) |
|---|---|
| `@st.cache` [Raghavendra, p186] | `@st.cache_data` · `@st.cache_resource` |
| `@st.experimental_memo` [p186] | `@st.cache_data` |
| `@st.experimental_singleton` [p187] | `@st.cache_resource` |
| `st.experimental_rerun()` [p179] | `st.rerun()` |

---

## 5. Cache × estado de sessão — a decisão

| | `@st.cache_data` | `st.session_state` |
|---|---|---|
| **Guarda** | o resultado de uma função | o que **este** usuário fez |
| **Indexado por** | os **argumentos** da chamada | a **chave** que você escolher |
| **Alcance** | **compartilhado** entre visitantes | **privado** da sessão |
| **Dura** | até o `ttl` vencer ou `.clear()` | a sessão (F5 começa outra) |
| **Some quando** | o servidor reinicia | a aba fecha |
| **Serve para** | não repetir trabalho **caro** | **atravessar** reruns |

### O teste que decide

> **Esse valor depende de QUEM está olhando?**
>
> - **Sim** → `st.session_state`
> - **Não, e é caro de calcular** → `@st.cache_data`
> - **Nem uma coisa nem outra** → variável comum

### Os dois erros simétricos

| Erro | O que acontece |
|---|---|
| Coleta cara em `session_state` | cada visitante paga a chamada de rede outra vez |
| **Dado do usuário em `@st.cache_data`** | **o próximo visitante vê o arquivo do anterior** |

O segundo não é um problema de performance: é **vazamento**. O livro é explícito sobre o cache ser
compartilhado:

> "…if that function is called with the same parameters **by another user**…, Streamlit does not run
> the same function but instead loads the result of the function from memory." [Richards, p83]

---

## 6. A "nuvem de palavras" que o TP2 pede

Por dentro, uma nuvem de palavras é uma **contagem**:

```python
from collections import Counter        # biblioteca padrão

contagem = Counter(
    palavra for palavra in palavras(texto)
    if len(palavra) >= 4 and sem_acento(palavra) not in PALAVRAS_VAZIAS
)
top = [{"palavra": p, "ocorrencias": n} for p, n in contagem.most_common(20)]
st.bar_chart(top, x="palavra", y="ocorrencias")
```

**Por que barras e não a nuvem:** a nuvem **não tem escala** — você vê que uma palavra é maior, mas
não sabe se é o dobro ou dez vezes. E `wordcloud` + `matplotlib` são duas dependências pesadas
(e o Community Cloud demora mais para construir). Se você quiser a nuvem desenhada, instale e
**declare no `requirements.txt`** — regra da Aula 5.

> **A lista de palavras vazias é sua.** *de, para, pelo, pode, grande…* — o que conta como "vazia" é
> **decisão editorial**, não um dado da natureza. Mantenha a lista **visível no seu código**, e
> revise-a **depois de ver o gráfico**. A nossa cresceu exatamente assim.

---

## 7. Anti-padrões desta aula

| Anti-padrão | Por que dói |
|-------------|-------------|
| `extend` no upload sem checar duplicata | a tabela cresce a cada rerun, sem erro nenhum |
| `try/except` espalhado pela interface em vez da borda | ilegível, e você acaba esquecendo um caso |
| Mensagem de erro não acionável ("arquivo inválido") | o usuário não sabe o que corrigir |
| **Cachear dado de um usuário** | vazamento: o próximo visitante vê o arquivo do anterior |
| Guardar em `session_state` o que é caro e igual para todos | cada visitante paga de novo |
| Memória "por precaução" | toda memória tem custo — de RAM e de depuração |
| `wordcloud` + `matplotlib` só pelo visual | duas dependências pesadas para um efeito |

---

## 8. Checklist de fechamento do TP2

- [ ] `venv` + `requirements.txt` completo + `.gitignore` *(Aula 5)*
- [ ] Repositório no GitHub, com histórico *(Aula 5)*
- [ ] App publicado no Streamlit Community Cloud, com URL *(Aula 5)*
- [ ] Interface com widgets, `st.form` e `st.session_state` *(Aula 6)*
- [ ] Script de scraping com **Beautiful Soup**, **executado à parte**, gravando **CSV/TXT em
      `data/`** *(Aula 7)* — com `robots.txt` verificado e a **fonte citada** no app
- [ ] **Upload** de CSV que complementa os dados já exibidos *(hoje)*
- [ ] **Download** do que está na tela *(hoje)*
- [ ] **Cache** (`@st.cache_data`) e **estado de sessão** (`st.session_state`), cada um no seu lugar *(hoje)*
- [ ] Estatísticas do texto / nuvem de palavras *(hoje)*
- [ ] **Project Charter** e **Data Summary Report** completos
- [ ] PDF `nome_sobrenome_PB_TP2.PDF` + **link do repositório** + **link do app no ar**

---

## 9. Fontes

- **RAGHAVENDRA, S.** *Beginner's Guide to Streamlit with Python*. Apress, 2023 — cap. 5
  (`download_button`, p123–124), cap. 6 (entradas e upload, p128), cap. 8 (`session_state`,
  p183–184; alertas, p176; caching, p185–187). **[A5, A8]**
- **RICHARDS, T.** *Streamlit for Data Science*, 2ª ed. Packt, 2023 — cap. 2 (*flow control*,
  p73–77; *caching*, p82–87; *Session State*, p91). **[B]**
- Documentação oficial do Streamlit — `st.cache_data.clear()`, `st.rerun()`, `column_config`.
