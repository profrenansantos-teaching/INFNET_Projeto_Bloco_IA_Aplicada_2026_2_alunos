# Aula 9 — Material de apoio do aluno
### Uma pergunta, uma página · PB Etapa 5 · subcompetência 3.1

> Consulte enquanto faz o **item 2 do TP3** (menu de navegação e múltiplas páginas). O checklist da
> seção 8 é o mesmo que o professor percorre no fim da aula.

---

## 1. A ideia que organiza tudo

É o **modelo de execução da Aula 6**, com uma segunda metade:

> A cada rerun o Streamlit roda o **roteador** (`app.py`) inteiro, de cima para baixo. Em
> `pagina.run()`, roda **a página escolhida — e só ela**. **Trocar de página é um rerun como outro
> qualquer.**

Medido no passo 2 (três cliques em Início, depois Indicadores): **roteador 4 · Início 3 ·
Indicadores 1**.

---

## 2. O jeito do livro: a pasta `pages/`

```
home.py          ← o arquivo do `streamlit run`      [Raghavendra, p172]
pages/
    page2.py     ← cada .py vira uma página            [Raghavendra, p173]
```

> "The way Streamlit creates multi-page apps is it looks in the same directory as our Streamlit app
> for a folder called pages and then runs each Python file inside the pages folder as its own
> Streamlit app." [Richards, p221]

**Funciona no Streamlit 1.61.** Mas o menu é a **listagem da pasta**: o nome no menu é o nome do
arquivo (o principal aparece como `home`), e renomear a página muda a **URL**. Prefixo numérico
(`1_…`) para ordenar e emoji no nome do arquivo para ícone são convenção do **Streamlit** —
**não** estão nos livros (Richards atribui emojis e seções à biblioteca de terceiros `st-pages`
[Richards, p224–225]).

---

## 3. O jeito de hoje: `st.navigation` + `st.Page`

```python
# app.py — o ROTEADOR
import streamlit as st

st.set_page_config(page_title="Meu painel", page_icon="🌱", layout="wide")   # uma vez, aqui

pagina = st.navigation({
    "Painel": [
        st.Page("paginas/inicio.py", title="Início", icon="🏠", default=True),
        st.Page("paginas/indicadores.py", title="Indicadores", icon="📊"),
    ],
    "Sobre o projeto": [
        st.Page("paginas/sobre.py", title="Dados e método", icon="ℹ️"),
    ],
})
pagina.run()          # roda a página escolhida — e SÓ ela
```

| Peça | O que faz |
|------|-----------|
| `st.Page(arquivo, title=, icon=, default=)` | declara uma página: o arquivo e o que o **menu** mostra |
| dicionário `{"Seção": [...]}` | agrupa as páginas em **seções** do menu (lista simples = sem seções) |
| `st.navigation(...)` | desenha o menu e **devolve** a página escolhida |
| `pagina.run()` | roda **só** a página escolhida |
| `position="top"` (opcional) | menu no topo, em vez da barra lateral |

- A **URL** de cada página vem do nome do arquivo: `paginas/indicadores.py` → `/indicadores`.
- Com `st.navigation`, a pasta `pages/` é **ignorada**. Escolha um mecanismo.
- **Rode de dentro da pasta do projeto:** os caminhos em `st.Page` são relativos ao `app.py`.

### Navegar por código

```python
st.page_link("paginas/indicadores.py", label="Indicadores", icon="📊")   # um link
if st.button("Ir para Dados e método"):
    st.switch_page("paginas/sobre.py")                                  # depois de uma ação
```

Os dois trocam de página **sem recarregar o navegador** — o `st.session_state` vai junto.

### ⚠️ Livro × hoje

| No livro (2023) | Hoje (Streamlit 1.61) |
|---|---|
| pasta `pages/` [Raghavendra, p171; Richards, p221] | `st.navigation` + `st.Page` |
| nome no menu = nome do arquivo | `title=` e `icon=` |
| seções/emojis só com `st-pages` [Richards, p224–225] | seções nativas; `position="top"` |
| "works only in Streamlit versions above 1.10" [Raghavendra, p174] | `st.navigation` desde a 1.36 |

---

## 4. O estado entre páginas — os dois defeitos que você VAI ter

### 🐛 4.1 O filtro que esquecia

Filtra em Indicadores, vai a outra página, volta: **o filtro voltou ao padrão**.

**Por quê:** no rerun em que um widget com `key` **não é desenhado**, o Streamlit **apaga** a chave
dele do `st.session_state`. Sair da página é esse rerun.

**Correção — no roteador, antes de `pagina.run()`:**

```python
CHAVES_PRESERVADAS = ("regioes", "populacao_minima", "criterio", "mostrar_tabela")

for chave in CHAVES_PRESERVADAS:
    if chave in st.session_state:
        st.session_state[chave] = st.session_state[chave]   # vira valor NOSSO; não é mais limpo
```

**E na página — um dono só para o valor inicial:**

```python
st.session_state.setdefault("regioes", todas_as_regioes)             # só grava na 1ª vez
regioes = st.multiselect("Regiões", todas_as_regioes, key="regioes") # SEM default=
```

Se você passar `default=` **e** regravar a chave, o terminal avisa: *"The widget with key "regioes"
was created with a default value but also had its value set via the Session State API."* — dois
donos para o mesmo valor.

### 🐛 4.2 O link direto que quebrava

Uma página lê uma chave que **outra** página cria. Pelo menu, na ordem, funciona. Pelo **link
direto**, numa aba nova (sessão nova):

```
AttributeError: st.session_state has no attribute "favoritas".
Did you forget to initialize it?
```

**Correção — toda chave que mais de uma página usa nasce no roteador:**

```python
def inicializar_estado():
    st.session_state.setdefault("favoritas", [])
    st.session_state.setdefault("noticias_enviadas", [])

inicializar_estado()      # no app.py, antes de pagina.run()
```

> **Como testar:** abra cada página pelo **link direto**, numa **aba anônima**. É uma sessão nova —
> é o que acontece com quem recebe o link.

---

## 5. Onde mora cada coisa

| O que está… | …acontece | Então coloque ali |
|---|---|---|
| no **roteador**, antes de `.run()` | em **toda** página, em todo rerun | configuração, **inicialização da memória**, preservação dos filtros, o menu |
| numa **página** | só quando ela é a escolhida | a análise daquela pergunta, e os widgets **dela** |
| em **`comum.py`** (importado) | quando alguma página chama | as **leituras caras**, com `@st.cache_data` |

### A leitura cara, uma vez

```python
# comum.py
@st.cache_data(ttl=3600)
def obter_dados():
    ...

# paginas/indicadores.py  e  paginas/comparador.py
from comum import obter_dados      # a MESMA função → o MESMO cache
```

**Não copie a função para cada página.** Medido no passo 4: *Tabela* **1.201 ms** → *Gráfico*
(mesma função) **0 ms** → *Cópia editada* **1.201 ms de novo**. Cópias idênticas até compartilham o
cache; basta uma divergir (até um `ttl` diferente) e a leitura roda duas vezes — **sem erro nenhum**.

---

## 6. Uma pergunta, uma página — e o que NÃO é página

O TP3: *"Cada página deve representar uma funcionalidade ou análise diferente."*

| Use… | quando… | Exemplo |
|------|---------|---------|
| **página** | é **outra pergunta** — outro trabalho do usuário | indicadores × notícias |
| **aba** (`st.tabs`) | é **outra vista da mesma resposta** | gráfico × tabela dos mesmos dados |
| **expander** | é **detalhe opcional** da mesma vista | o formulário de envio de CSV |

> Abas servem para *"showing one piece of content at a time"* [Richards, p208]. Mas atenção
> (verificado): por padrão, **o código de todas as abas roda em todo rerun** — a aba só esconde.
> Numa página, só a escolhida roda.

**Não é "uma página por gráfico".** 27 páginas, uma por UF, é um seletor fingindo de menu.

---

## 7. Anti-padrões desta aula

| Anti-padrão | Por que dói |
|-------------|-------------|
| memória compartilhada inicializada **numa página** | o link direto de outra página quebra |
| testar só entrando pelo Início | o usuário real chega pelo link |
| `default=` **e** chave regravada no mesmo widget | dois donos; o Streamlit avisa |
| copiar a função cacheada para cada página | a primeira edição dobra o custo, em silêncio |
| filtro na barra lateral comum que não filtra nada naquela página | ensina a desconfiar dos filtros |
| uma página por gráfico (ou por UF) | menu que ninguém lê |
| roteador que desenha análise | ela aparece em **toda** página |

---

## 8. Checklist do TP3 — o que dá para entregar depois de hoje

- [ ] **Menu de navegação + múltiplas páginas** — cada página responde a **uma pergunta** (escreva-a
      no topo da página)
- [ ] O **link direto** de cada página abre sem erro numa aba anônima
- [ ] Os filtros sobrevivem à troca de página (se o seu app tem filtros)
- [ ] As leituras caras definidas **uma vez** (`comum.py`) e importadas
- [ ] O **arquivo principal continua `app.py`**, e `paginas/` + `comum.py` estão no repositório
      (`git status`)
- [ ] **Project Charter revisado** — o que mudou no problema e nas metas com a Etapa 5
- [ ] *(Aula 10)* Selenium, **se necessário** · *(Etapa 6)* API com FastAPI — o TP3 fecha lá

---

## 9. Fontes

- **RAGHAVENDRA, S.** *Beginner's Guide to Streamlit with Python*. Apress, 2023 — cap. 7 (*Sidebars*,
  p170–171; **Multipage Navigation**, p171–174). **[A7]**
- **RICHARDS, T.** *Streamlit for Data Science*, 2ª ed. Packt, 2023 — cap. 6 (*tabs*, p208–210;
  *sidebar*, p210–212; **Multi-page apps**, p220–225); cap. 2 (*Session State*, p92). **[B]**
- Documentação oficial do Streamlit — `st.navigation`, `st.Page`, `st.page_link`, `st.switch_page`.
  Verificados por execução (Streamlit 1.61), em 23/09/2026.
