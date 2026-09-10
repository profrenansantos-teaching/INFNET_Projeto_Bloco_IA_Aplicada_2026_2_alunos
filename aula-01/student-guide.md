# Aula 1 — Material de Apoio do Aluno
### Introdução ao planejamento de projeto de Ciência de Dados

Bem-vindo(a) ao Projeto de Bloco! Este guia acompanha a Aula 1. Leia o "antes da aula", use a
**cola de código** durante o encontro e siga o **checklist do TP1** depois. 🌱

> **Como este bloco funciona.** Ele foi desenhado para quem vem **direto do bloco de entrada**: assumimos
> que você já programa em **Python básico** (listas, dicionários, `for`, funções). Vamos introduzir
> ferramentas novas **só quando forem necessárias**, sempre explicando o porquê. Nos primeiros contatos,
> trabalhamos os dados em **Python puro** (listas e dicionários) — **pandas fica para depois**. E você é
> encorajado a usar **IA como copiloto** (ver o fim deste guia).

---

## Antes da aula — o que ler (≈ 40 min)
| Leitura | Por quê | Foque em | Chegue sabendo |
|---------|---------|----------|----------------|
| GEORGE, cap. 1 (*Practical Data Science with Python*) | apresenta CRISP-DM e TDSP | "Data science project methodologies" (p45–48) | o que é CRISP-DM e por que existe método |
| MICROSOFT — *Team Data Science Process (lifecycle)* | fonte oficial do TDSP | os 5 estágios e seus objetivos | nomes dos 5 estágios do TDSP |
| ESPPENCHUTZ, cap. 4–5 (*Data Ingestion with Python Cookbook*) | tipos de dados | estruturado / semi / não-estruturado; JSON | por que JSON é semi-estruturado |
| RAGHAVENDRA, cap. 1–2 (*Beginner's Guide to Streamlit*) | primeira app + elementos de texto/tabela | "Creating Our First App"; `st.title`, `st.write`, `st.dataframe` | como rodar `streamlit run` |

**Perguntas-guia (o encontro parte delas):**
1. Qual a diferença entre o *tema* de um projeto e o seu *problema de negócio*?
2. O que torna uma pergunta "afiada" — e de que *tipo* ela pode ser?
3. CRISP-DM e TDSP competem ou se complementam? Como um mapeia no outro?
4. Qual a diferença entre dado estruturado, semi-estruturado e não-estruturado?
5. Como você representaria uma tabela de dados usando só listas e dicionários?

---

## Em aula — o que esperar
Arco de 90 min: gancho + progressão → objetivos → **problema de negócio** (você rascunha o seu) →
**CRISP-DM e TDSP** (voto em par) → **estrutura, artefatos e dados em Python puro** → **código guiado** da
primeira app Streamlit → bilhete de saída. Traga o notebook com Python instalado.

---

## Conceitos-chave (para revisar)
**Os 4 elementos do problema de negócio**
1. **Pergunta afiada** — específica, relevante, não ambígua (boa o bastante para dizer *qual dado buscar*).
2. **Meta/KPI** — como medir sucesso, com número e prazo. *Output* (entregar o painel) ≠ *outcome* (a decisão apoiada).
3. **Público-alvo** — quem **usa** e quem **decide**.
4. **ODS atendido** — a qual Objetivo da Agenda 2030 você contribui, e por quê.

**Tipos de pergunta em ciência de dados** (o tipo define o que o projeto entrega):
| Tipo | Responde | Exige |
|------|----------|-------|
| Descritiva | O que aconteceu? | coletar + agregar + visualizar |
| Diagnóstica | Por que aconteceu? | cruzar/comparar variáveis |
| Preditiva | O que vai acontecer? | modelo/estatística |
| Prescritiva | O que fazer? | otimização/recomendação |
Nosso painel começa **descritivo** — e descritivo bem feito já apoia decisão.

**Método: CRISP-DM (6 fases, cíclico)**
Entendimento do Negócio → Entendimento dos Dados → Preparação → Modelagem → Avaliação → Implantação.
Cada fase tem um **entregável** e uma **armadilha** típica (ex.: na Avaliação, medir só a acurácia técnica
em vez do KPI de negócio).

**Método: TDSP (5 estágios, iterativo)** — evolução do CRISP-DM (papéis, template de repo, iteração):
Business Understanding → Data Acquisition and Understanding → Modeling → Deployment → Customer Acceptance.

**CRISP-DM ↔ TDSP (o mesmo esqueleto):** Negócio = Business Understanding · Dados+Preparação = Data
Acquisition & Understanding · Modelagem = Modeling · Avaliação+Implantação = Deployment + Customer Acceptance.

**Artefatos iniciais:** **Project Charter** (escopo, objetivos, KPIs, ODS, público, riscos) e
**Data Summary Report** (fontes, tipo e objetivo de uso).

**Tipos de dados:** **estruturado** (tabelas/CSV/SQL), **semi-estruturado** (JSON/XML — típico de APIs),
**não-estruturado** (texto/áudio/vídeo). Fio do projeto: a API do IBGE devolve **JSON (semi)** → viramos
**tabela (estruturado)** para comparar UFs.

**Dados em Python puro:** uma **linha** é um **dicionário**; a **tabela** é uma **lista de dicionários**.

---

## Cola de código — Python puro + Streamlit (sem pandas)
> Instale o ambiente uma vez; depois é só `streamlit run app.py`.

```bash
# 1) ambiente isolado do projeto
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 2) dependência (só isto)
pip install streamlit

# 3) rodar (abre em http://localhost:8501)
streamlit run app.py
```

```python
import csv
import streamlit as st

# set_page_config PRECISA ser a primeira chamada Streamlit do script
st.set_page_config(page_title="Painel ODS Brasil", layout="wide")

st.title("Painel de Indicadores Sustentáveis do Brasil")
st.subheader("Dados abertos a serviço da Agenda 2030")
st.markdown("[API do IBGE](https://servicodados.ibge.gov.br/api/docs)")  # markdown + links

# ---- dados em Python puro: uma lista de dicionários (cada linha = 1 dict) ----
def carregar_amostra(caminho):
    linhas = []
    with open(caminho, encoding="utf-8") as arquivo:
        for linha in csv.DictReader(arquivo):          # cada linha já vira um dict
            linha["populacao_2025"] = int(linha["populacao_2025"])  # texto -> inteiro
            linhas.append(linha)
    return linhas

dados = carregar_amostra("data/sample/populacao_amostra.csv")

# ---- resumos com Python puro (len, set, sum) ----
c1, c2, c3 = st.columns(3)
c1.metric("UFs", len({l["uf"] for l in dados}))
c2.metric("Regiões", len({l["regiao"] for l in dados}))
c3.metric("População", f'{sum(l["populacao_2025"] for l in dados):,}'.replace(",", "."))

# ---- tabela: st.dataframe aceita a LISTA DE DICIONÁRIOS direto (sem pandas) ----
st.dataframe(dados, use_container_width=True, hide_index=True)
# st.table(dados)  # alternativa ESTÁTICA
```

**Dicas rápidas**
- `st.dataframe`/`st.table` aceitam **estruturas nativas** (lista de dicionários) — nada de pandas por ora.
- `st.dataframe` = interativo (ordena/rola) · `st.table` = estático.
- Salvou o arquivo? A página oferece **Rerun** / **Always rerun**.
- Erro? O Streamlit mostra o traceback na **própria página** — leia a última linha.

---

## IA como copiloto (prática encorajada)
Use ChatGPT/Copilot/Claude para **gerar** e **explicar** código — por exemplo: *"como somar uma coluna de
uma lista de dicionários em Python?"*. É ótimo para aprender e destravar. **Regra de ouro:** você precisa
**entender e saber explicar** cada linha que entregar. Se não sabe explicar, não entregue — pergunte à IA
*"por quê?"* até entender.

---

## Checklist do TP1 (Parte 1 desta aula)
- [ ] Problema de negócio escrito nos **4 elementos** (pergunta afiada, KPI, público, ODS).
- [ ] Estrutura de diretórios criada (espelha o TDSP: `data/`, `docs/`, `src/`, `app.py`, `requirements.txt`).
- [ ] **Project Charter** (primeira versão) em `docs/`.
- [ ] **Data Summary Report** (esboço das fontes de dados) em `docs/`.
- [ ] App demo em Streamlit com **título, descrição, links e tabela de amostra**, rodando localmente.

---

## Autoteste (respostas no fim)
1. Transforme em *pergunta afiada* e classifique o **tipo**: "quero ajudar o meio ambiente".
2. Quantas fases tem o CRISP-DM? E o TDSP? Como o Entendimento do Negócio do CRISP-DM mapeia no TDSP?
3. JSON é estruturado, semi-estruturado ou não-estruturado? E um CSV?
4. Como você representa uma tabela de dados em Python puro?
5. Qual função Streamlit exibe uma tabela **interativa**? Ela precisa de pandas?
6. Por que usar um ambiente virtual (`venv`)?

<details><summary>Respostas</summary>

1. Ex.: "Quais UFs estão mais atrás em saneamento e deveriam ser priorizadas?" — **descritiva** (aponta o dado).
2. CRISP-DM = **6**; TDSP = **5**. Entendimento do Negócio ↔ **Business Understanding**.
3. **JSON = semi-estruturado**; **CSV = estruturado** (tabular).
4. Como uma **lista de dicionários** — cada linha é um dicionário `{coluna: valor}`.
5. `st.dataframe(...)` (a `st.table(...)` é estática). **Não** precisa de pandas — aceita a lista de dicionários.
6. Para isolar as versões/bibliotecas do projeto, garantir reprodutibilidade e registrar o que ele precisa.
</details>
