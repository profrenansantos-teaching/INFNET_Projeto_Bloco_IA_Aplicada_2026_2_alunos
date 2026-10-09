# Aula 10 — Material de apoio do aluno
### Quando o dado chega depois · PB Etapa 5 · subcompetência 3.2

> Consulte enquanto faz o **item 3 do TP3** — *"utilize o Selenium… **se necessário**"*. A seção 1
> ajuda a decidir se é necessário; o resto, a fazer bem feito se for.

---

## 1. Primeiro: precisa mesmo?

### Diagnóstico em 3 minutos, no próprio navegador

| Ferramenta | Mostra | Se o dado aparece aqui… |
|------------|--------|-------------------------|
| **Exibir código-fonte** (Ctrl+U) | o HTML que o **servidor mandou** — o que o `requests` recebe | …**degrau 2**: `requests` + BeautifulSoup (Aula 7) |
| **F12 → Rede** (Network) → *Fetch/XHR* → recarregar | as requisições que a **página** faz depois de carregar | …**degrau 3**: `requests` direto no JSON |
| **F12 → Elementos** (Inspecionar) | o DOM **depois** do JavaScript | …e só aqui: **degrau 4**, navegador pilotado |

### A escada

| Degrau | Quando | Exemplo no curso |
|--------|--------|------------------|
| **1 · API documentada** | existe contrato escrito | IBGE (Aula 2) |
| **2 · HTML estático** | o dado está no código-fonte | Agência Brasil (Aula 7) |
| **3 · JSON por trás da página** | a aba Rede mostra de onde o dado vem | `rates2025.json` do PRODES |
| **4 · Selenium** | o dado só existe depois do JS, ou exige interação/*token* | o painel do PRODES (v8) |
| **X · não coletar** | `robots.txt` proíbe; termos proíbem; exige sua conta pessoal | — |

> *"The use of Selenium is preferred (**many times, even as a last option**) in specific cases or when
> scraping is not possible with other libraries and techniques."* [Chapagain, p195]

**Regra:** suba **um** degrau só quando o de baixo não serve — e **escreva o motivo** no Data Summary
Report. O TP3 avalia a **decisão**, não o Selenium.

---

## 2. Instalar

```bash
pip install selenium            # e ter o Google Chrome instalado
```

O **driver** (ChromeDriver), o próprio Selenium baixa na primeira execução (**Selenium Manager**). O
livro baixa à mão, pareando versões [Chapagain, p197–199] — não é mais necessário.

**No seu projeto, dois arquivos de requisitos:**

```
requirements.txt          # o app — o que o Community Cloud instala. SEM selenium.
requirements-coleta.txt   # -r requirements.txt
                          # selenium>=4.20
```

**O padrão do curso:** o app **não** abre navegador — ele lê o CSV que a coleta gravou. O Community
Cloud não traz Chrome; dá para instalar (seção 7), mas custa. Se o app não importa o `selenium`, ele
não vai para o `requirements.txt` do app.

---

## 3. Abrir, ir, fechar

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

opcoes = webdriver.ChromeOptions()
opcoes.add_argument("--headless=new")          # sem janela (tire para VER o Chrome)

with webdriver.Chrome(options=opcoes) as driver:
    driver.get(URL)
    ...
# aqui o navegador já foi fechado — mesmo se deu erro
```

| Peça | O que faz |
|------|-----------|
| `driver.get(url)` | carrega a página — e volta quando ela **carrega**, **não** quando o JavaScript termina |
| `driver.find_element(By.CSS_SELECTOR, "…")` | **um** elemento (erro se não achar) [Chapagain, p204] |
| `driver.find_elements(By.CSS_SELECTOR, "…")` | uma **lista** (vazia se não achar) |
| `.text` · `.get_attribute("href")` · `.click()` | ler texto · ler atributo · clicar [Chapagain, p205–206] |
| `driver.page_source` | o HTML **depois** do JavaScript [Chapagain, p202] |
| `driver.quit()` | fecha **tudo** — sempre num `finally`, ou use `with` |

Localizadores `By`: `ID`, `CSS_SELECTOR`, `XPATH`, `NAME`, `TAG_NAME`, `CLASS_NAME`, `LINK_TEXT`,
`PARTIAL_LINK_TEXT` [Chapagain, p205]. No curso: **CSS** — o mesmo seletor do `select()` do
BeautifulSoup.

---

## 4. Esperar — a parte que decide tudo

**Medido na página de exercício (as 9 linhas chegam uma a uma):**

| Estratégia | Linhas | Veredito |
|------------|:------:|----------|
| sem espera | 0/9 | leu antes de o JS começar |
| `time.sleep(1)` | 0/9 | chute; com 5 s acertaria — e custaria 5 s **sempre** |
| espera **implícita** (`driver.implicitly_wait(10)`) | **1/9** | `find_elements` volta com **o primeiro** elemento — **lista pela metade, sem erro** |
| espera **explícita** (`WebDriverWait` + condição) | **9/9** | ✅ |

> ⚠️ O livro só mostra a implícita e a chama de *"the sleep time"* [Chapagain, p201]. **Não é.** Ela
> diz ao driver: toda busca pode esperar **até achar algum** elemento.

### A espera explícita

```python
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

esperar = WebDriverWait(driver, 30)          # tenta a cada 0,5 s, até 30 s

esperar.until(EC.text_to_be_present_in_element((By.ID, "status"), "carregadas"))
esperar.until(EC.element_to_be_clickable((By.ID, "mais")))           # antes de CLICAR
esperar.until(EC.presence_of_element_located((By.CSS_SELECTOR, "…")))  # ⚠️ ver abaixo
```

Se a condição não vale no tempo-limite: **`TimeoutException`**. Isso é bom — a coleta **quebra em voz
alta** em vez de gravar dado incompleto.

### ⚠️ Presença do elemento ≠ presença do dado

No painel do PRODES, quando o `get()` volta (~1,5 s), a `<table>` **já existe — vazia**. As linhas
chegam ~1 s depois. Esperar pela tabela devolveu **0 linhas**. Espere pela **condição do dado**:

```python
def tabela_completa(d):                      # qualquer função (driver) -> verdadeiro/falso serve
    ufs = d.find_elements(By.CSS_SELECTOR, "#tb-area tr.dc-table-group")
    return len(ufs) >= 9                     # um FATO do domínio: a Amazônia Legal tem 9 UFs

esperar.until(tabela_completa)
```

### Depois de cada ação, espere de novo

```python
botao = esperar.until(EC.element_to_be_clickable((By.ID, "mais")))   # o botão, não só o dado
botao.click()                                                        # o clique NÃO devolve o dado
esperar.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "#tabela tbody tr")) >= 18)
```

---

## 5. Extrair com o BeautifulSoup — o que você já sabe

```python
html = driver.page_source                       # o HTML DEPOIS do JavaScript
# … daqui para baixo, nada de Selenium: é a Aula 7
sopa = BeautifulSoup(html, "html.parser")
for tr in sopa.select("#tabela tbody tr"):
    celulas = [td.get_text(strip=True) for td in tr.find_all("td")]
```

**Por quê:** a função que recebe **HTML** é testável **sem navegador e sem rede**, sobre o snapshot.
O Selenium só serve para **rodar o JavaScript**.

---

## 6. O coletor completo (o esqueleto da v8)

```python
def baixar_renderizado(url):
    driver = abrir_navegador()
    try:
        driver.get(url)
        esperar_tabela(driver)               # a CONDIÇÃO do dado
        html = driver.page_source
    finally:
        driver.quit()                        # SEMPRE
    (RAW / "snapshot.html").write_text(html, encoding="utf-8")   # data/raw/ — não versionado
    return html

linhas = extrair_tabela(html)                # BeautifulSoup
problema = conferir(linhas)                  # a guarda da Aula 7
if problema:
    sys.exit(f"NÃO gravei: {problema}")      # a coleta boa de ontem continua lá
gravar(linhas)                               # data/processed/ — versionado; o app lê daqui
```

Rode **à parte**: `python -m src.coleta_dinamica`. O app só lê o CSV.

---

## 7. E se eu PRECISAR do Selenium no app publicado? (aprofundamento)

**Dá.** O Community Cloud roda em Debian e instala os pacotes listados num **`packages.txt` na raiz do
repositório**:

```text
chromium
chromium-driver
```

(sem comentários no arquivo — cada linha vai para o instalador do sistema). O `selenium` entra no
`requirements.txt` **do app**, porque agora o app o importa. O exemplo completo e testado está em
`aula-10-step-by-step/passo06_selenium_no_app/`. As três escolhas que o tornam viável:

```python
@st.cache_data(ttl=3600)                 # 1) uma coleta por hora, para TODOS os visitantes
def coletar_ao_vivo():
    try:
        with abrir_navegador() as driver:     # 2) abre e FECHA aqui — nada de st.cache_resource
            ...
    except Exception as erro:
        return [], str(erro)                  # 3) a falha também vai para o cache
    return linhas, ""

# abrir_navegador(): --headless=new --no-sandbox --disable-dev-shm-usage --disable-gpu;
# no servidor, Service(shutil.which("chromedriver")) — o driver que o packages.txt instalou.
```

- **Sem o cache**, seria um Chrome por rerun. **Com o navegador em `st.cache_resource`**, ele ficaria
  aberto para sempre e seria dividido entre sessões. **Exceção não vai para o cache** (verificado) — por
  isso a falha é devolvida, e não levantada.
- **Medido aqui:** 1ª coleta 6,1 s, reruns 0 ms; um Chrome sem janela ocupa **380–640 MB**. O app no
  Community Cloud tem **de 690 MB a 2,7 GB** (documentação do Streamlit, fev/2024).
- **Riscos:** *build* frágil (há relatos de `chromium-driver` não encontrado, jun/2025); o servidor não
  está no Brasil (há sites que bloqueiam por localização); após 12 h sem acesso o app hiberna, e o
  primeiro visitante paga a coleta.

> **Vale quando** o dado precisa ser mais fresco que a última coleta. Para o TP3, quase nunca — e a
> coleta à parte continua sendo o padrão.

---

## 8. Ética e licença

- **O `robots.txt` vale para o navegador pilotado.** Ele é um robô. *"The ethical duty of all
  developers"* [Chapagain, p100].
- **Não disfarce o robô.** O Chrome sem janela se anuncia como `HeadlessChrome` — deixe assim.
  Contornar medidas anti-bot, CAPTCHA ou login alheio **não** é coleta: é invasão.
- **Leia a licença.** CC BY (Agência Brasil): cite. **CC BY-SA** (INPE): cite **e** compartilhe o
  derivado sob a mesma licença.

---

## 9. Anti-padrões desta aula

| Anti-padrão | Por que dói |
|-------------|-------------|
| Selenium como primeiro degrau | segundos e memória onde um `requests` bastava; o TP3 cobra a decisão |
| `time.sleep` como espera | lento sempre, errado no dia em que o site demorar mais |
| espera pela **presença** do elemento | o elemento pode existir vazio: 0 linhas, sem erro |
| espera implícita + `find_elements` | lista pela metade, sem erro |
| clicar sem esperar o **clicável** | `ElementNotInteractableException` |
| `quit()` fora do `finally` | navegadores esquecidos (medido: 3 erros → 3 Chromes abertos) |
| gravar sem guarda | a coleta incompleta de hoje apaga a completa de ontem |
| Selenium no app **sem cache** | um Chrome novo a cada rerun, para cada visitante |
| navegador guardado em `st.cache_resource` | fica aberto para sempre, dividido entre sessões |
| `selenium` no `requirements.txt` de um app que não o importa | peso morto no *build* |
| disfarçar o robô | é a linha entre coletar e invadir |

---

## 10. Checklist do item 3 do TP3

- [ ] **Diagnóstico feito:** código-fonte → aba Rede → Inspecionar. Em que degrau está a sua fonte?
- [ ] **Decisão escrita** no Data Summary Report: *por que não o degrau de baixo?* (se não precisou
      de Selenium, escreva isso — é uma resposta válida e, muitas vezes, a melhor)
- [ ] Se usou Selenium: espera **explícita** pela condição do dado · `with`/`finally` · extração com
      BeautifulSoup sobre o `page_source` · **guarda** antes de gravar · snapshot em `data/raw/`
- [ ] Dados em **CSV/TXT em `data/`**, coletados **à parte**; o app só lê
- [ ] `selenium` em `requirements-coleta.txt` — e só no `requirements.txt` do app **se o app o
      importar** (seção 7, com `packages.txt` e cache)
- [ ] `robots.txt` verificado · licença lida e citada no app

---

## 11. Fontes

- **CHAPAGAIN, A.** *Hands-On Web Scraping with Python*, 2ª ed. Packt, 2023 — cap. 8 (*Using Selenium
  to Scrape the Web*, p192–213); cap. 3 (`robots.txt`, p100–102). **[R8]**
- Documentação oficial do Selenium — `WebDriverWait`, `expected_conditions`, Selenium Manager,
  *headless*. Verificados por execução (Selenium 4.49, Chrome 153), em 23/09/2026.
- Documentação oficial do Streamlit — `packages.txt` (dependências do sistema) e limites de recursos
  do Community Cloud (fev/2024).
- INPE. **PRODES — TerraBrasilis**, taxas anuais de desmatamento na Amazônia Legal. CC BY-SA 4.0.
