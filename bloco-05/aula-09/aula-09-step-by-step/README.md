# Aula 9 — Passo a passo: uma pergunta, uma página

> Cada passo é um **app multipáginas completo e independente**, numa pasta própria. Rode, mexa,
> entenda — só então vá ao próximo. O destino é a **v7** em `../demo/painel_ods_brasil/`.
> **Nenhum passo precisa de internet.**

Num app multipáginas o comando é dado **de dentro da pasta do passo**, porque o caminho de cada
página é relativo ao arquivo principal:

```bash
cd passo02_roteador
streamlit run app.py
```

| Passo | Pasta · arquivo principal | O que ensina | Subcomp. |
|------:|---------------------------|--------------|----------|
| **1** | `passo01_do_jeito_do_livro/` · `home.py` | a pasta `pages/` [Raghavendra, p171–173]: o menu é a **listagem da pasta** e os nomes vêm dos **arquivos** | 3.1 |
| **2** | `passo02_roteador/` · `app.py` | `st.navigation` + `st.Page`: o **roteador roda em todo rerun**; só a página escolhida roda; `st.page_link` e `st.switch_page` | 3.1 |
| **3** | `passo03_estado_entre_paginas/` · `app.py` | os **dois tropeços** da v7: o filtro que **esquecia** e o link direto que **quebrava** | 3.1 |
| **4** | `passo04_cache_compartilhado/` · `app.py` | a leitura cara **definida uma vez** e importada; a **cópia** que paga de novo | 3.1 |
| **5** | `../demo/painel_ods_brasil/` · `app.py` | tudo junto, no Painel ODS — a **v7** | 3.1 |

---

## A ideia que amarra os quatro passos

É o **modelo de execução da Aula 6**, estendido — e é só isso:

> A cada rerun, o Streamlit roda o **roteador** (`app.py`) inteiro, de cima para baixo. Quando chega
> em `pagina.run()`, roda **a página escolhida — e só ela**. Trocar de página é um rerun como outro
> qualquer.

Daí saem as três regras da v7:

| O que está… | …acontece | Então coloque ali |
|---|---|---|
| no **roteador**, antes de `.run()` | em **toda** página, em todo rerun | configuração, **inicialização da memória**, preservação dos filtros, o menu |
| numa **página** | só quando ela é a escolhida | a análise daquela pergunta, e os widgets **dela** |
| em **`comum.py`** (importado) | quando alguma página chama | as **leituras caras** cacheadas — uma definição, um cache |

## Passo 1 · O jeito do livro

```bash
cd passo01_do_jeito_do_livro
streamlit run home.py
```

O menu mostra **home** · **Indicadores** · **page2**. Os três nomes vêm dos **arquivos**: para
renomear uma página, renomeia-se o arquivo (e a URL muda junto). O prefixo `1_` ordena e o emoji vira
ícone — convenção de nome de arquivo do **Streamlit** (verificada no 1.61; **não** está nos livros,
que atribuem emojis e seções à biblioteca de terceiros `st-pages` [Richards, p224–225]).
**Funciona no Streamlit 1.61**; só não é mais o caminho recomendado.

## Passo 2 · O roteador

Clique no botão da página Início algumas vezes e compare os dois contadores: o do **roteador** sobe
sempre; o da **página** só quando ela está aberta. Depois experimente os dois jeitos de navegar por
código:

```python
st.page_link("paginas/indicadores.py", label="Indicadores", icon="📊")   # um link
if st.button("Ir"):
    st.switch_page("paginas/sobre.py")                                  # por código
```

## Passo 3 · Os dois tropeços

**O filtro que esquecia.** Com o interruptor *Preservar os filtros* **desligado**: escolha só
*Nordeste*, vá a *Outra página*, volte → **as cinco regiões voltaram**. Ligue o interruptor e repita
→ o filtro fica.

> **Por quê:** no rerun em que um widget com `key` **não é desenhado**, o Streamlit **apaga** a chave
> dele do `st.session_state`. Sair da página *é* esse rerun. A correção — regravar a chave no
> roteador — faz o Streamlit tratá-la como valor **nosso**, e não como estado do widget.

**O link direto que quebrava.** Mude `INICIALIZAR_NO_ROTEADOR` para `False`, salve, e abra numa
**aba nova** `http://localhost:8501/memoria` → `AttributeError: st.session_state has no attribute
"marcadas"`. Na aba antiga, onde você já passou por *Filtros*, tudo funciona — **é isso que esconde o
defeito**: quem desenvolve sempre entra pela porta da frente.

## Passo 4 · A leitura cara, uma vez

Abra *Tabela* (**≈ 1.200 ms**), depois *Gráfico* (**0 ms** — a mesma função, o mesmo cache), depois
*Cópia* (**≈ 1.200 ms de novo**). O contador da barra lateral vai de **1** para **2**.

> A cópia **idêntica** até compartilharia o cache. Mas cópias **divergem** — basta alguém editar uma
> delas — e aí o cache passa a ser outro, e a leitura cara roda duas vezes, **sem erro nenhum**.

## Números medidos (não estimados)

| Onde | Medição |
|------|---------|
| Passo 2 · 3 cliques em Início, depois Indicadores | roteador **4** · Início **3** · Indicadores **1** |
| Passo 3 · Nordeste → outra página → volta | desligado: **as 5 regiões**; ligado: **Nordeste** |
| Passo 3 · link direto de /memoria sem inicializar | **`AttributeError`**; pela porta da frente: **funciona** |
| Passo 4 · Tabela → Gráfico → Cópia | **1.201 ms** → **0 ms** → **1.201 ms** · contador **1 → 1 → 2** |

Verificado com `AppTest` (Streamlit 1.61) e num navegador real (Chrome 153, headless) em 23/09/2026.

## Depois dos quatro passos

```bash
cd ../demo/painel_ods_brasil
streamlit run app.py
```

No app v7, faça o roteiro:

1. em **Indicadores**, filtre só o *Nordeste* e aplique;
2. vá a **Comparador**, marque **SP** e **BA** → aparece o aviso de que SP está fora do filtro que
   você deixou em Indicadores (uma página lendo o que o usuário fez na outra);
3. vá a **Notícias** e volte a **Indicadores** → o filtro **continua** *Nordeste*;
4. abra **Dados e método** → a tabela *A memória desta sessão* mostra tudo o que você fez nas outras
   páginas.
