# Aula 2 — Passo a Passo: Coleta de Dados via API + Streamlit

> Pasta com os **7 passos** da Aula 2, começando do `requests.get()` mais simples até o app Streamlit completo com gráfico e filtros.
> Cada passo roda SOZINHO, usa **dados salvos em JSON** (não depende de rede) e te mostra EXATAMENTE o que cada parte do código faz.

---

## Como usar (ordem recomendada)

| Passo | Arquivo | O que aprende | Como rodar |
|-------|---------|---------------|------------|
| **1** | [passo01_chamada_basica.py](passo01_chamada_basica.py) | `requests.get` → status → `.json()` → estrutura de 1 UF | `python passo01_chamada_basica.py` |
| **2** | [passo02_lista_para_dicionario.py](passo02_lista_para_dicionario.py) | Lista → dicionário `por_id` (busca rápida por id de UF) | `python passo02_lista_para_dicionario.py` |
| **3** | [passo03_json_aninhado.py](passo03_json_aninhado.py) | Navegar JSON profundo: `[0]["resultados"][0]["series"]` | `python passo03_json_aninhado.py` |
| **4** | [passo04_montar_tabela.py](passo04_montar_tabela.py) | Loop nas séries + tratar tipos (`int(...)`) → 27 linhas finais | `python passo04_montar_tabela.py` |
| **5** | [passo05_camada_de_dados.py](passo05_camada_de_dados.py) | Isolar em `src/data_access.py` + fallback (cache) | `python passo05_camada_de_dados.py` |
| **6** | [passo06_app_inicial.py](passo06_app_inicial.py) | App Streamlit básico: título + métricas + tabela | `streamlit run passo06_app_inicial.py` |
| **7** | [passo07_app_final.py](passo07_app_final.py) | App final: cache + filtro região + gráfico barras | `streamlit run passo07_app_final.py` |

---

## Os 6 JSONs de dados reais (pasta `dados/`)

Todos foram coletados DA API REAL do IBGE e salvos para você rodar os passos sem precisar de rede.

| Arquivo | O que contém | Vem do Passo |
|---------|--------------|--------------|
| [dados/passo01_ufs_resposta_bruta.json](dados/passo01_ufs_resposta_bruta.json) | Lista com as 27 UFs (id, sigla, nome, **região aninhada**) | API de Localidades |
| [dados/passo02_ufs_por_id.json](dados/passo02_ufs_por_id.json) | Dicionário `{id: {uf, estado, regiao}}` para busca O(1) | Resultado do Passo 2 |
| [dados/passo03_populacao_resposta_bruta.json](dados/passo03_populacao_resposta_bruta.json) | Resposta INTEIRA e aninhada da API de Agregados | API SIDRA /agregados/6579 |
| [dados/passo03b_populacao_series.json](dados/passo03b_populacao_series.json) | Só a parte que importa: as 27 séries (1 por UF) | Extração do Passo 3 |
| [dados/passo04_linhas_finais.json](dados/passo04_linhas_finais.json) | TABELA final (27 dicionários com uf, estado, regiao, populacao_2025) | Resultado do Passo 4 |
| [dados/ufs_cache.json](dados/ufs_cache.json) | Igual ao acima, mas com `{"periodo": "2025", "linhas": [...]}` — formato do fallback | Usado no Passo 5 |

Também temos uma cópia em `data/sample/ufs_cache.json` para ser igual à estrutura do demo.

---

## Fluxo lógico (o que conecta cada passo)

```
Passo 1  →  UFs (lista de 27 dicts) → salvo em passo01_ufs_resposta_bruta.json
    ↓
Passo 2  →  transforma em dicionário por_id  →  salvo em passo02_ufs_por_id.json
    ↓
Passo 3  →  chamo SIDRA, navego até series  →  salvo em passo03b_populacao_series.json
    ↓
Passo 4  →  LOOP: junta por_id + series, corrige os tipos (int!) → 27 linhas finais
    ↓
Passo 5  →  isola tudo isso em funções no src/data_access.py com fallback para cache
    ↓
Passo 6  →  importo carregar_dados() e mostro tudo no Streamlit (básico)
    ↓
Passo 7  →  adiciono @st.cache_data, st.multiselect(filtro) e st.bar_chart (gráfico)
```

---

## Dicas para estudar com esses passos

1. **Leia o `print` de cada passo.** Eles explicam, em português, o que acabou de acontecer — é aí
   que está a aula, não só no código.
2. **Sem rede? Nenhum problema.** Só os passos 1 e 3 chamam a API do IBGE; quando perguntarem,
   escolha a **opção 2 (arquivo salvo)**. Todos os outros leem os JSONs da pasta `dados/`.
3. **Quer dados mais novos do IBGE?** Rode `_coletar_dados_reais.py` para regravar os JSONs da
   pasta `dados/` com as respostas atuais da API.

---

## Requisitos

```bash
pip install streamlit requests
# ou
pip install -r ../demo/painel_ods_brasil/requirements.txt
```
