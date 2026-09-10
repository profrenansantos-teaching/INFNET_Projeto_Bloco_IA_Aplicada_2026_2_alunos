"""
PASSO 6 — App Streamlit INICIAL (carrega dados → mostra na tela)
Corresponde a: §4 (sem cache, sem filtros, sem gráfico ainda).

Objetivo do Passo 6: VER que o app roda e os dados chegam.
Nenhuma enfeite — só o básico funcionando.

Rode:  streamlit run passo06_app_inicial.py
"""

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

import streamlit as st
from src.data_access import carregar_dados

# 1) Configuração da página (sempre a PRIMEIRA chamada do Streamlit!)
st.set_page_config(page_title="Painel ODS Brasil — Passo 6", page_icon="🌱", layout="wide")

# 2) Título e subtítulo
st.title("🌱 Painel ODS Brasil")
st.subheader("Passo 6 · Versão INICIAL (sem cache, sem filtros, sem gráfico)")

# 3) Carregar os DADOS (usa a camada do Passo 5)
st.info("💡 Carregando dados a partir de `src/data_access.carregar_dados()`...")
dados, fonte = carregar_dados()

# 4) Mostrar de onde vieram os dados (API ou cache?)
st.caption(f"Fonte: {fonte} · {len(dados)} UFs carregadas")

# 5) 3 métricas simples (Python puro — sem pandas!)
col1, col2, col3 = st.columns(3)
col1.metric("Total de UFs", len(dados))
col2.metric("Regiões do Brasil", len({linha["regiao"] for linha in dados}))

chave_pop = [k for k in dados[0].keys() if "populacao" in k][0]
total_pop = sum(linha[chave_pop] for linha in dados)
col3.metric("População total (soma)", f"{total_pop:,}".replace(",", "."))

# 6) Tabela com TODOS os dados
st.markdown("### 📋 Todas as UFs (dados crus)")
st.dataframe(dados, use_container_width=True, hide_index=True)

# 7) Exemplo de 1 linha detalhada
st.markdown("### 🔎 Como é 1 linha (1 dicionário Python)")
st.code(f"# linha[0] = \n{repr(dados[0])}", language="python")

st.success("""
✅ Passo 6 funcionando! O app já:
   1. Carrega 27 UFs via API (ou fallback)
   2. Mostra 3 métricas de resumo
   3. Mostra a tabela completa

Próximo passo (7): + cache + filtro por região + gráfico de barras.
""")
