"""
Passo 6 (APROFUNDAMENTO, com rede) — Selenium DENTRO do app publicado, do jeito menos caro.

O padrão do curso é coletar À PARTE e o app só ler o CSV (v8). Mas dá, sim, para o
app abrir um navegador — inclusive no Streamlit Community Cloud, que não traz Chrome
mas instala o Chromium se o repositório tiver um packages.txt (ver README desta pasta).

Se for para fazer, faça assim:

  1. @st.cache_data(ttl=3600) na COLETA — o navegador abre no máximo uma vez por
     hora, para todos os visitantes juntos (o cache é compartilhado: Aula 8).
     Sem isso, seria um Chrome por rerun.
  2. O navegador abre e FECHA dentro da função cacheada (with). NÃO o guarde em
     @st.cache_resource: ele ficaria aberto para sempre ocupando centenas de MB,
     e seria o MESMO navegador para duas sessões ao mesmo tempo.
  3. A falha também é cacheada (devolvemos o erro em vez de levantá-lo). Exceção
     não vai para o cache — e uma coleta que falha abriria um Chrome a cada rerun.
  4. A guarda de sempre: 9 UFs, ou não serve.

Rodar (de dentro desta pasta):   streamlit run app.py
Publicar: este app.py, requirements.txt e packages.txt na RAIZ de um repositório.
"""

import shutil
import time
from datetime import datetime

import streamlit as st
from bs4 import BeautifulSoup

URL = "https://terrabrasilis.dpi.inpe.br/app/dashboard/deforestation/biomes/legal_amazon/rates"
FONTE = "INPE/PRODES — TerraBrasilis · CC BY-SA 4.0"


def abrir_navegador():
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service

    opcoes = webdriver.ChromeOptions()
    opcoes.add_argument("--headless=new")           # no servidor não há tela: obrigatório
    opcoes.add_argument("--no-sandbox")             # exigido em contêiner Linux
    opcoes.add_argument("--disable-dev-shm-usage")  # /dev/shm pequeno no contêiner
    opcoes.add_argument("--disable-gpu")
    # No Community Cloud, o packages.txt instala o chromium-driver no PATH, pareado
    # com o Chromium do sistema. Na sua máquina, não há — e o Selenium Manager resolve.
    driver_do_sistema = shutil.which("chromedriver")
    if driver_do_sistema:
        return webdriver.Chrome(options=opcoes, service=Service(driver_do_sistema))
    return webdriver.Chrome(options=opcoes)


def extrair(html: str) -> list[dict]:
    """A tabela renderizada -> [{estado, ano, area_km2}]. BeautifulSoup, como na Aula 7."""
    linhas, estado = [], None
    for tr in BeautifulSoup(html, "html.parser").select("table#tb-area tbody tr"):
        if "dc-table-group" in tr.get("class", []):
            estado = tr.find("b").get_text(strip=True)
        elif estado:
            ano, area = [td.get_text(strip=True) for td in tr.find_all("td")][:2]
            numero = area.replace("km²", "").replace(".", "").replace(",", ".").strip()
            linhas.append({"estado": estado, "ano": int(ano), "area_km2": float(numero)})
    return linhas


@st.cache_data(ttl=3600, show_spinner="Abrindo um navegador e coletando o PRODES (~5–10 s)…")
def coletar_ao_vivo():
    """Devolve (linhas, erro, segundos, quando). NUNCA levanta: a falha também vai para
    o cache, senão cada rerun de cada visitante abriria um Chrome novo tentando de novo."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait

    inicio = time.perf_counter()
    quando = datetime.now().strftime("%d/%m/%Y %H:%M")
    try:
        with abrir_navegador() as driver:            # abre AQUI e fecha ao sair do with
            driver.get(URL)
            WebDriverWait(driver, 60, poll_frequency=0.25).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, "#tb-area tr.dc-table-group")) >= 9,
                message="as 9 UFs não apareceram em 60 s",
            )
            html = driver.page_source
    except Exception as erro:                        # sem Chrome, rede fora, site mudou…
        return [], f"{type(erro).__name__}: {str(erro).splitlines()[0][:200]}", \
            time.perf_counter() - inicio, quando

    linhas = extrair(html)
    if len({linha["estado"] for linha in linhas}) < 9:
        return [], "a tabela veio sem as 9 UFs", time.perf_counter() - inicio, quando
    return linhas, "", time.perf_counter() - inicio, quando


st.title("🌳 Selenium dentro do app (aprofundamento)")
st.caption("A coleta acontece aqui, no servidor do app — uma vez por hora, para todos os visitantes.")

relogio = time.perf_counter()
linhas, erro, custo_coleta, coletado_em = coletar_ao_vivo()
custo_agora = time.perf_counter() - relogio

a, b, c = st.columns(3)
a.metric("Custo da coleta (quando rodou)", f"{custo_coleta:.1f} s")
b.metric("Custo NESTE rerun", f"{custo_agora * 1000:.0f} ms")
c.metric("Coletado em", coletado_em)

if erro:
    st.error(
        f"A coleta ao vivo falhou: {erro}. O resultado da falha fica em cache por 1 hora "
        "para não abrir um navegador a cada clique. É exatamente por isso que o padrão do "
        "curso é coletar À PARTE e o app só ler o CSV."
    )
    if st.button("Tentar de novo agora"):
        coletar_ao_vivo.clear()
        st.rerun()
    st.stop()

totais: dict[int, float] = {}
for linha in linhas:
    totais[linha["ano"]] = totais.get(linha["ano"], 0.0) + linha["area_km2"]
serie = [{"ano": str(ano), "area_km2": area} for ano, area in sorted(totais.items())]

st.metric(f"Amazônia Legal, {max(totais)}", f"{totais[max(totais)]:,.0f} km²".replace(",", "."))
st.line_chart(serie, x="ano", y="area_km2", x_label="Ano", y_label="km² desmatados")
st.caption(f"{len(linhas)} linhas coletadas agora, com Selenium, de {FONTE}.")
