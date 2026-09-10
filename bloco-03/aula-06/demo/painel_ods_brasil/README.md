# Painel de Indicadores Sustentáveis do Brasil — v4

Demo do **Projeto de Bloco: Inteligência Artificial Aplicada** (INFNET) · **Aula 6 · PB Etapa 3**.

Painel ESG/ODS com dados abertos do **IBGE**, em **Python puro** (sem pandas).
Esta versão (**v4**) acrescenta à v3 a **camada de interação**: formulário de filtros, memória de
sessão, controle de fluxo e exportação. **A coleta não mudou** — publicar a v4 é um `git push`.

## Rodar localmente

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows  ·  source .venv/bin/activate no macOS/Linux
pip install -r requirements.txt
streamlit run app.py
```

Camadas rodáveis sem interface (é o ponto: elas não dependem do Streamlit):

```bash
python -m src.data_access      # coleta as 27 UFs (ou usa o cache)
python -m src.transformacoes   # filtra, ordena, resume, compara e exporta CSV
```

## O que mudou da v3 para a v4

| # | Mudança | Ferramenta | Por quê |
|---|---------|-----------|---------|
| 1 | Quatro filtros enviados em **lote** | `st.form` + `st.form_submit_button` | 4 mexidas = **1** rerun, não 4 [Raghavendra, p157] |
| 2 | **Comparador** de UFs — tabela com % do Brasil, posição no ranking nacional e distância para a maior marcada | `st.session_state` | as UFs marcadas **sobrevivem à mudança de filtro**; com variável comum a comparação se perderia a cada rerun [Richards, p87–91] |
| 3 | Filtro sem resultado **avisa** em vez de quebrar | `st.stop()` + `st.warning` | [Raghavendra, p178 · Richards, p77] |
| 4 | Usuário **leva a tabela embora** | `st.download_button` + módulo `csv` | terceiro pedido da gestora |
| 5 | Espera visível na coleta | `st.spinner` | [Raghavendra, p126] |
| 6 | Lógica separada da interface | **`src/transformacoes.py`** | funções puras, testáveis no terminal |

## Estrutura — três camadas

```
painel_ods_brasil/
├── app.py                          INTERFACE   — o que perguntar e o que mostrar
├── src/
│   ├── data_access.py              DADOS       — de onde vêm (API do IBGE + fallback)
│   └── transformacoes.py           LÓGICA      — filtrar, ordenar, resumir, exportar
├── data/sample/ufs_cache.json      cache de emergência (fallback)
├── requirements.txt · .gitignore · DEPLOY.md   (infraestrutura, da Aula 5)
└── .streamlit/config.toml · secrets.toml.example
```

`src/transformacoes.py` **não importa Streamlit**. É essa fronteira que torna a lógica testável e o
app fácil de mudar: trocar a interface não obriga a reescrever a regra de negócio.

## Widgets usados (e onde)

| Widget | Onde | O que devolve |
|--------|------|---------------|
| `st.multiselect` | regiões (no form) | uma **lista** |
| `st.slider` | população mínima (no form) | um número |
| `st.radio` | critério de ordenação (no form) | a opção escolhida |
| `st.checkbox` | mostrar/esconder a tabela (no form) | `True`/`False` |
| `st.form_submit_button` | "Aplicar filtros" | `True` no rerun do envio |
| `st.selectbox` + `st.button` | comparador (**fora** do form) | UF escolhida · `True` no clique |
| `st.download_button` | exportar CSV | — |
| `st.metric` · `st.bar_chart` · `st.dataframe` | métricas, gráfico e tabelas (inclusive a do comparador) | — |

> ⚠️ O comparador está **fora** do formulário porque `st.button` comum **não pode** ficar dentro de um
> `st.form` (verificado: levanta `StreamlitAPIException`).

## Por que o comparador existe (e por que ele usa a base completa)

`comparar()` recebe **`dados`** (as 27 UFs), não `filtrados`. Isso é deliberado:

- uma UF marcada **continua na comparação** mesmo quando o filtro atual a exclui;
- é exatamente essa persistência que **justifica** o `st.session_state`. Se a comparação morresse a
  cada mudança de filtro, uma variável comum bastaria — e o recurso viraria enfeite.

A tabela acrescenta três números que **só existem na comparação**: participação na população do país,
posição no ranking nacional e a distância para a maior das UFs marcadas. Sem eles, o "comparador" seria
uma lista de siglas — o anti-padrão do *painel de avião* que a própria aula ensina a evitar.

## Publicar

O mesmo repositório da Aula 5 — o roteiro completo está em [`DEPLOY.md`](DEPLOY.md):

```bash
git add .
git commit -m "v4: filtros em formulário, comparador e download"
git push
```

Recarregue a URL em 1–2 minutos. O rodapé mostra `v4 — Aula 6 (interatividade)`.

## Verificação

Comportamentos confirmados por `AppTest` (Streamlit 1.61), não por leitura:

- dois cliques em *Comparar* acumulam → `['SP', 'AC']`, e a tabela do comparador vem com 2 linhas;
- **filtrando só o Sudeste, o AC continua no comparador** e o app avisa
  *"No comparador, mas fora do filtro atual: AC"* — é a prova de que o `session_state` está fazendo
  trabalho real, e não enfeite;
- *Limpar comparador* zera a lista;
- filtro impossível (Norte + 40 M) → `st.warning` e **nenhuma** métrica renderizada (o `st.stop`
  funciona);
- ordenar por nome reordena as opções do comparador → `['ES', 'MG', 'RJ', 'SP']`;
- render inicial sem exceção e sem aviso de descontinuação.

## Configuração

Igual à v3: `PAINEL_ODS_VERIFICAR_SSL` (ambiente) ou `verificar_ssl` (`secrets.toml`) — padrão
**seguro**. Ver `DEPLOY.md`, seção 7.
