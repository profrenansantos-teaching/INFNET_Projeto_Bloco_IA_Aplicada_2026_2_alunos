# Aula 6 — Passo a passo: o painel responde ao usuário

> Cada passo é um app Streamlit **completo e independente**. Rode, mexa nos controles, entenda o
> comportamento — só então vá ao próximo. O destino é a **v4** em `../demo/painel_ods_brasil/`.

```bash
streamlit run passo01_widgets_basicos.py
```

| Passo | Arquivo | O que ensina | Fonte |
|------:|---------|--------------|-------|
| **1** | `passo01_widgets_basicos.py` | button · radio · checkbox · selectbox · multiselect — **o widget devolve um valor** | Raghavendra, cap. 5 (p114–123) |
| **2** | `passo02_slider_e_entradas.py` | slider (simples e de intervalo) · number_input · text_input · date_input · color_picker | doc. oficial + Raghavendra, cap. 6 (p128–134) |
| **3** | `passo03_rerun.py` | **o modelo de execução**: cada interação roda o script inteiro | Richards, p87 |
| **4** | `passo04_form.py` | `st.form` + `st.form_submit_button` — 4 mexidas, **1** rerun | Raghavendra, p157 |
| **5** | `passo05_session_state.py` | `st.session_state` — a lista que lembra | Richards, p87–91 · Raghavendra, p183–184 |
| **6** | `passo06_fluxo_e_feedback.py` | alertas · `st.stop` · spinner · progress · `st.download_button` | Richards, p73–77 · Raghavendra, p125–126, p176–178 |
| **7** | `../demo/painel_ods_brasil/app.py` | tudo junto, no Painel ODS — a **v4** | — |

---

## A ideia que amarra os seis passos

Um widget em Streamlit **não dispara um evento**. Ele é uma **expressão que devolve o valor
escolhido** — e, a cada interação, o Streamlit **reexecuta o arquivo inteiro, de cima para baixo**,
com o novo valor.

```python
regiao = st.selectbox("Região", ["Norte", "Sudeste"])   # regiao JÁ É a escolha
```

> "1. By default, information is not stored across reruns of the app.
> 2. On user input, Streamlits are rerun top-to-bottom." — [Richards, p87]

Dessa única regra saem **todas** as consequências práticas:

| Consequência | Ferramenta | Passo |
|--------------|-----------|-------|
| Variável comum é zerada a cada rerun | `st.session_state` | 3, 5 |
| Coleta cara seria refeita a cada rerun | `@st.cache_data` | (Aula 2) |
| 4 filtros = 4 reruns | `st.form` | 4 |
| Não faz sentido desenhar a tela agora | `st.stop()` | 6 |

## Experimentos que valem a pena fazer (não só ler)

1. **Passo 3:** clique 5 vezes no contador de variável comum. Ele **nunca** passa de 1. Só depois
   disso o `session_state` faz sentido.
2. **Passo 4:** anote o contador de reruns; mexa nos quatro widgets da esquerda (sobe 4); recarregue,
   mexa nos quatro da direita e clique em *Aplicar* (sobe 1).
3. **Passo 5:** favorite duas UFs no bloco "sem memória" — a primeira some. Depois faça o mesmo no
   bloco com `session_state`.
4. **Passo 6:** arraste o slider até o fim. Em vez de um gráfico vazio ou de uma exceção, você recebe
   uma instrução do que fazer.
5. **Qualquer passo:** aperte **F5**. Tudo em `session_state` desaparece — é memória de **sessão**.

## Armadilhas que você vai encontrar (todas reais)

| Sintoma | Causa | Correção |
|---------|-------|----------|
| `KeyError: 'favoritas'` | usou `st.session_state.favoritas` sem inicializar | `if "favoritas" not in st.session_state: st.session_state.favoritas = []` |
| `StreamlitAPIException` no `st.slider` | `min_value == max_value` (a base filtrou até sobrar um valor) | garanta faixa de largura ≥ 1 — ver `faixa_populacao()` em `src/transformacoes.py` |
| `StreamlitAPIException: st.button() can't be used in an st.form()` | só o **submit** é permitido dentro de um form | tire o botão para fora do bloco |
| `StreamlitAPIException: st.form_submit_button() must be used inside an st.form()` | submit solto, fora de qualquer form | mova-o para dentro do `with st.form(...)` |
| O formulário aparece, mas **nada acontece** ao mexer nele | `st.form` **sem** `st.form_submit_button` | acrescente o submit. ⚠️ Verificado no Streamlit 1.61: isso **não levanta erro** — só não funciona. É o pior tipo de defeito. |
| A mensagem do `st.button` some sozinha | `st.button` devolve `True` só no rerun do clique | guarde o efeito em `st.session_state` |
| Duas UFs favoritadas, só a última aparece | lista recriada a cada rerun | `st.session_state` (passo 5) |
| Widgets iguais em telas diferentes se atropelam | chaves duplicadas | passe `key="algo_único"` |

## Do passo 7 ao ar

A **v4** roda no mesmo repositório publicado na Aula 5. Para colocar as novidades no ar:

```bash
git add .
git commit -m "v4: filtros em formulário, favoritas e download"
git push
```

Recarregue a URL. É o ciclo da Aula 5 — agora com algo visível para mostrar.
