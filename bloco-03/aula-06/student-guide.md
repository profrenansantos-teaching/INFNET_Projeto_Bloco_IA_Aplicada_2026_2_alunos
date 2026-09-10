# Aula 6 — Material de Apoio do Aluno
### O painel responde ao usuário · PB Etapa 3 · subcompetência 2.2

Seu painel está no ar desde a Aula 5 — e é **mudo**: mostra exatamente o recorte que **você** escolheu.
Hoje ele ganha **controles, formulário e memória**. E cada melhoria vai ao ar com um `git push`. 🎛️

> **Padrão do bloco:** Python puro (**sem pandas**); código **guiado**; **IA como copiloto** (usar,
> desde que você entenda e saiba explicar). Traga o **projeto publicado** da Aula 5.

## Antes da aula (≈ 35 min)

**Fazer:**

- [ ] Ter o app da Aula 5 **publicado** e a URL à mão (se travou, traga a **mensagem de erro exata**)
- [ ] Rodar o projeto localmente: `streamlit run app.py`

**Ler:**

| Leitura | Por quê | Foque em |
|---------|---------|----------|
| RAGHAVENDRA, cap. 5 ("Buttons and Sliders") | fonte principal | `button` (p114), `radio` (p115), `checkbox` (p117), `selectbox` (p119), `multiselect` (p121), `download_button` (p123) |
| RAGHAVENDRA, cap. 6 ("Forms") | formulário | `text_input` (p129), `number_input` (p133), `form_submit_button` (p157) |
| RICHARDS, cap. 2 — "Persistence with Session State" | **o conceito-chave** | os dois fatos da p87; a lista de tarefas que esquece (p87–90); `st.session_state` (p91) |

**Perguntas-guia:** (1) O que acontece com as variáveis do seu script quando o usuário clica num botão?
(2) Por que `st.button` devolve `True` só uma vez? (3) Para que serve agrupar filtros num formulário?
(4) O que sobrevive a um rerun?

## A regra que explica tudo

Um widget em Streamlit **não dispara um evento**. Ele é uma **expressão que devolve o valor escolhido**
— e, a cada interação, o Streamlit **reexecuta o arquivo inteiro, de cima para baixo**.

```python
regiao = st.selectbox("Região", ["Norte", "Sudeste"])   # regiao JÁ É a escolha
```

> "1. By default, information is not stored across reruns of the app.
> 2. On user input, Streamlits are rerun top-to-bottom." — [Richards, p87]

### O que sobrevive a um rerun

| Sobrevive | Não sobrevive |
|-----------|---------------|
| `st.session_state` | variáveis comuns do script |
| resultado de `@st.cache_data` | resultado de função sem cache |
| valor do widget (ligado à sua chave) | qualquer coisa recalculada no topo |

Dessa regra saem **todas** as ferramentas de hoje:

| Consequência | Ferramenta |
|--------------|-----------|
| Variável comum é zerada a cada rerun | `st.session_state` |
| Coleta cara seria refeita a cada rerun | `@st.cache_data` (você já usa desde a Aula 2) |
| 4 filtros mexidos = 4 reexecuções | `st.form` |
| Não faz sentido desenhar a tela agora | `st.stop()` |

## Catálogo de widgets

| Widget | Devolve | Exemplo |
|--------|---------|---------|
| `st.button("Favoritar")` | `True` **só** no rerun do clique | ação pontual |
| `st.radio("Ordenar por", opcoes)` | a opção escolhida | critério de ordenação |
| `st.checkbox("Mostrar tabela", value=True)` | `True`/`False` | mostrar/esconder |
| `st.selectbox("UF", ufs)` | **uma** opção | escolher um item |
| `st.multiselect("Regiões", regioes, default=regioes)` | **uma lista** | filtrar vários |
| `st.slider("Mínimo", 0, 50_000_000, 0, step=100_000)` | número (ou **tupla**, se `value` for tupla) | faixa numérica |
| `st.number_input("Top N", 1, 27, 10, 1)` | número | mín, máx, padrão, passo |
| `st.text_input("Buscar", max_chars=40)` | texto | busca |
| `st.download_button("Baixar", data=csv, file_name="x.csv")` | — | levar o resultado embora |

> ⚠️ **Nota de fonte.** O cap. 5 chama-se "Buttons and Sliders" mas **não traz exemplo de
> `st.slider`** fora de `st.sidebar` — o resumo do próprio autor (p127) confirma. O que ensinamos sobre
> `st.slider` vem da **documentação oficial**, verificado no demo. Checar a fonte — inclusive o livro —
> faz parte do trabalho.

## Cola de código

```python
# ---- formulário: 4 filtros, 1 rerun ----
with st.form("filtros"):
    regioes = st.multiselect("Regiões", disponiveis, default=disponiveis)
    minimo  = st.slider("População mínima", pop_min, pop_max, pop_min, step=100_000)
    criterio = st.radio("Ordenar por", ["População", "Nome"])
    mostrar  = st.checkbox("Mostrar tabela", value=True)
    aplicar  = st.form_submit_button("Aplicar filtros")   # o form precisa dele
```

```python
# ---- memória: inicializar ANTES de usar ----
if "favoritas" not in st.session_state:
    st.session_state.favoritas = []

if st.button("Comparar"):
    if uf not in st.session_state.favoritas:
        st.session_state.favoritas.append(uf)

# ...e a memória tem de SERVIR para alguma coisa. Aqui ela alimenta uma
# comparação montada a partir da base COMPLETA — por isso uma UF marcada
# continua no comparador mesmo quando o filtro atual a exclui:
comparadas = comparar(dados, st.session_state.favoritas)   # `dados`, não `filtrados`
```

> **O teste antes de criar estado:** *o que o usuário perde se isso for jogado fora a cada rerun?*
> Se a resposta for "nada", não é estado — é enfeite, e você acabou de construir um
> "painel de avião" (o anti-padrão da própria aula).

```python
# ---- fluxo: responder bem ao caso vazio ----
if not filtrados:
    st.warning("Nenhuma UF atende a esses filtros. "
               "Diminua a população mínima ou selecione mais regiões.")
    st.stop()          # nada abaixo é executado
```

```python
# ---- levar o resultado embora (Python puro, sem pandas) ----
import csv, io
buffer = io.StringIO()
w = csv.DictWriter(buffer, fieldnames=list(filtrados[0].keys()))
w.writeheader(); w.writerows(filtrados)
st.download_button("Baixar CSV", data=buffer.getvalue(),
                   file_name="painel.csv", mime="text/csv")
```

## ⚠️ APIs do livro que envelheceram

O livro-texto é de 2023 e algumas funções mudaram de nome. **Use a coluna da direita:**

| No livro | Hoje |
|----------|------|
| `@st.cache` | `@st.cache_data` (dados) · `@st.cache_resource` (conexões/modelos) |
| `@st.experimental_memo` | `@st.cache_data` |
| `@st.experimental_singleton` | `@st.cache_resource` |
| `st.experimental_rerun()` | `st.rerun()` |
| `st.experimental_show()` | `st.write()` (para depurar) |

**A lição maior:** livro, tutorial e resposta de IA envelhecem. O hábito é **rodar, ler o aviso de
descontinuação e conferir na documentação**.

## Armadilhas (todas reais — aconteceram construindo o demo)

| Sintoma | Causa | Correção |
|---------|-------|----------|
| Marquei duas UFs, só a última aparece | lista recriada a cada rerun | `st.session_state` |
| `KeyError: 'favoritas'` no 1º acesso | usou o estado sem inicializar | `if "favoritas" not in st.session_state: ...` |
| `StreamlitAPIException` no `st.slider` | `min_value == max_value` | garanta faixa de largura ≥ 1 |
| `st.button()` can't be used in an `st.form()` | botão comum dentro do form | tire-o para fora |
| O formulário aparece mas nada acontece | `st.form` **sem** `st.form_submit_button` | acrescente o submit — **isso não dá erro, só não funciona** |
| A mensagem do botão some sozinha | `st.button` é `True` só no rerun do clique | guarde o efeito em `st.session_state` |
| Dois widgets se atropelam | chaves duplicadas | passe `key="algo_único"` |

## Passo a passo executável

Seis apps independentes em `aula-06-step-by-step/` — rode, mexe, entenda:

```bash
streamlit run passo03_rerun.py       # clique 5x no contador comum: nunca passa de 1
streamlit run passo04_form.py        # conta os reruns dos dois lados
streamlit run passo05_session_state.py
```

## IA como copiloto

Boa pergunta: *"explique por que esta lista não acumula entre cliques no Streamlit"*.
Má prática: pedir o app pronto. **Peça também que a IA diga qual versão do Streamlit está assumindo** —
metade dos exemplos que ela produz usa `@st.cache` e `st.experimental_rerun`, que não valem mais.

## Checklist do TP2 (parte desta aula)

- [ ] 2–3 parâmetros expostos ao usuário, **justificados** (e um que você decidiu **não** expor)
- [ ] Filtros agrupados em `st.form` com `st.form_submit_button`
- [ ] Caso vazio tratado com `st.stop()` + aviso **acionável**
- [ ] Ao menos um uso de `st.session_state`, inicializado antes do uso — **e que faça alguma coisa**
      (você precisa saber dizer o que o usuário perde sem ele)
- [ ] `git push` feito e a mudança **visível na URL publicada**

## Autoteste

1. O usuário clica 3 vezes num botão que faz `total += 1`, com `total = 0` na linha acima. O que aparece?
2. O que `st.session_state` guarda, e por quanto tempo?
3. Quando um formulário é a escolha errada?
4. Por que `st.slider` pode derrubar o app quando os limites vêm dos dados?
5. Dois colegas abrem a URL do seu app. Eles compartilham o `session_state`?
6. Qual a diferença entre um defeito que **quebra** e um que **engana**?

<details><summary>Respostas</summary>

1. **1.** A linha `total = 0` é reexecutada em **todo** rerun, antes do `if`. Cada clique zera e soma 1.
2. Um **dicionário global da sessão** do usuário: dura enquanto a aba estiver aberta. **F5 apaga**
   [Raghavendra, p183].
3. Quando você **quer** resposta imediata a cada mexida — um único seletor, uma busca ao vivo. O
   formulário adia o resultado; isso só compensa se as entradas fizerem sentido **juntas** ou se cada
   rerun for caro.
4. Se o filtro reduzir a base a um único valor, `min_value == max_value` e o widget levanta exceção.
   Widget que recebe parâmetro **calculado** precisa de guarda.
5. **Não.** Cada usuário tem a própria sessão. `session_state` não é banco de dados.
6. O que **quebra** você descobre na hora; o que **engana** ninguém descobre — até alguém tomar uma
   decisão com o número errado. O segundo é mais perigoso.

</details>
