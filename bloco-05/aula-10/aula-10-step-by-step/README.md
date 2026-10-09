# Aula 10 — Passo a passo: quando o dado chega depois

> Os passos 1–5 são **scripts** (não apps Streamlit): no padrão do curso, o Selenium roda **fora** do
> app. O passo 6 (aprofundamento) mostra o outro caminho — o navegador **dentro** do app publicado.
> O destino é a **v8** em `../demo/painel_ods_brasil/`. **Os passos 1 a 4 não precisam de internet** —
> eles usam `pagina_dinamica.html`, uma página de exercício que imita o painel do PRODES: chega com a
> tabela **vazia**, e o JavaScript a preenche **linha a linha**. O passo 5 é o painel real.

**Antes:** instale o ambiente da coleta (a partir da pasta do demo) e tenha o **Google Chrome**
instalado. O driver, o Selenium baixa sozinho na primeira execução (Selenium Manager).

```bash
pip install -r ../demo/painel_ods_brasil/requirements-coleta.txt
python passo01_a_casca.py
```

| Passo | Arquivo | O que ensina | Rede? |
|------:|---------|--------------|:-----:|
| **1** | `passo01_a_casca.py` | o que o `requests`/BeautifulSoup enxergam: a **tabela vazia** (`--online`: a casca do PRODES, 3.098 bytes) | não (opcional) |
| **2** | `passo02_o_navegador.py` | abrir o Chrome sem janela, ir, ler, **fechar** (`with`); o User-Agent diz **HeadlessChrome** | não |
| **3** | `passo03_as_esperas.py` | **quatro esperas** lado a lado — só a **explícita** traz as 9 linhas | não |
| **4** | `passo04_clicar_e_extrair.py` | **clicar**, esperar de novo, `page_source` → **BeautifulSoup** → guarda → CSV | não |
| **5** | `passo05_a_escada.py` | a **escada** no painel real: casca → **JSON por trás** → Selenium, e a **conferência** entre as rotas | **sim** |
| **6** | `passo06_selenium_no_app/` · `streamlit run app.py` | **aprofundamento:** Selenium **dentro** do app publicado — `packages.txt`, cache, falha cacheada | **sim** |
| **7** | `../demo/painel_ods_brasil/` | tudo junto: `python -m src.coleta_dinamica` → a página 🌳 no app — a **v8** | sim |

---

## A ideia que amarra os passos

> O `driver.get()` espera a página **carregar** — não espera o **JavaScript terminar**. Entre as duas
> coisas mora todo o problema desta aula. **Espere pela condição do dado, não pela presença do
> elemento** — e pelo que você vai **usar**, não pelo que você acha que basta.

E uma divisão de trabalho que não muda:

| Ferramenta | Faz | Não faz |
|------------|-----|---------|
| **Selenium** | abre o navegador, roda o JavaScript, clica, espera | extrair (dá, mas é pior de testar) |
| **BeautifulSoup** | extrai do `page_source` — o que já sabemos da Aula 7 | rodar JavaScript |

## Passo 3 · as quatro esperas (o coração da aula)

| Estratégia | Tempo | Linhas | Por quê |
|------------|------:|:------:|---------|
| A · sem espera | 0,1 s | **0/9** | leu antes de o JS começar |
| B · `time.sleep(1)` | 1,1 s | **0/9** | chute: a 1ª linha chega aos ~1,05 s. Com `sleep(5)` acertaria — e custaria 5 s **sempre** |
| C · espera **implícita** (a do livro) | 1,2 s | **1/9** | `find_elements` volta quando existe **o primeiro** elemento — **lista pela metade, sem erro** |
| D · espera **explícita** (a condição) | 3,7 s | **9/9** | `WebDriverWait` até o status dizer "9 UFs carregadas" |

> **O livro só mostra a implícita** [Chapagain, p201], descrita como *"the sleep time… before any
> further action is taken"* — o que ela **não** é. `WebDriverWait` não aparece no capítulo. A
> divergência é **ensinada**, como a do `lxml` na Aula 7.

## Passo 4 · 🐛 esperar pelo dado ≠ esperar pela ação

A primeira versão esperava as 9 linhas e clicava: **`ElementNotInteractableException`**. A 9ª linha
aparece **250 ms antes** de a página mostrar o botão. Correção: `EC.element_to_be_clickable` antes de
clicar. **Espere pelo que você vai USAR.**

## Passo 5 · a escada, ao vivo (com rede)

| Degrau | O que fazemos | Resultado (23/09/2026) |
|--------|---------------|------------------------|
| 1 · `requests` na página | a casca | 3.098 bytes, nenhum dado |
| 3 · o JSON por trás (aba **Rede**) | `rates2025.json` + o arquivo que traduz códigos | 342 pares (UF, ano) |
| 4 · Selenium | a tabela renderizada | 342 pares (UF, ano) |
| conferência | degrau 4 × degrau 3 | **zero diferenças** |

> *(O degrau 2 — HTML estático — é o que a casca descartou.)* Conferir uma rota contra a outra é o
> jeito mais barato de saber que a extração está certa.

## Passo 6 · e se eu QUISER o Selenium no app publicado? (aprofundamento)

O padrão do curso é a coleta à parte. Mas o Streamlit Community Cloud **não traz navegador e instala
um** se o repositório tiver, **na raiz**, um `packages.txt` (uma linha por pacote, sem comentários):

```text
chromium
chromium-driver
```

A pasta `passo06_selenium_no_app/` é um app completo, pronto para ser a raiz de um repositório:
`app.py` + `requirements.txt` (com `selenium`, porque agora o app o importa) + `packages.txt`.

```bash
cd passo06_selenium_no_app
streamlit run app.py
```

**Três escolhas** tornam isso viável — e cada uma evita um defeito que custa caro no servidor:

| Escolha | Sem ela |
|---------|---------|
| `@st.cache_data(ttl=3600)` na coleta | um Chrome por rerun, para cada visitante |
| navegador **aberto e fechado** dentro da função (`with`) | em `st.cache_resource`, ficaria aberto para sempre e dividido entre sessões |
| a **falha também vai para o cache** (devolvida, não levantada) | exceção não é cacheada: cada rerun abriria um Chrome novo tentando de novo |

**Verificado localmente:** 1ª coleta **6,1 s**, reruns **0 ms**, **nenhum** navegador aberto depois;
coleta que falha: servida do cache em **0,01 s** no rerun. **Não verificado no Community Cloud** — o
`packages.txt` é documentado pelo Streamlit, a dupla `chromium` + `chromium-driver` vem de projetos de
referência, e há relatos no fórum de `chromium-driver` não encontrado (jun/2025). O preço está no
`../demo/painel_ods_brasil/DEPLOY.md` §10.1.

## Números medidos (não estimados)

| Onde | Medição |
|------|---------|
| Passo 1 `--online` | TerraBrasilis via `requests`: **3.098 bytes**, texto visível `'TerraBrasilis'`, 0 tabelas |
| Passo 2 | abrir o Chrome: **~2 s**; logo após o `get()`: **0 linhas**; 4 s depois: **9** |
| Passo 3 (3 execuções, sempre igual) | A 0/9 · B 0/9 · **C 1/9** · D 9/9 |
| Passo 4 | 9 → clique → **18 linhas** → `saida_passo04.csv` |
| Passo 5 | **342 × 342, zero diferenças** |
| Laço de coleta com erro, **sem** `finally` | 3 erros → **3 navegadores** esquecidos abertos; com `with` → **0** |
| Passo 6 (local) | 1ª coleta **6,1 s** · reruns **0 ms** · **0** navegadores abertos depois · falha cacheada: **0,01 s** |
| Memória de um Chrome sem janela | **380 MB** vazio · **~640 MB** com o PRODES (Windows, RSS somado) |
| `@st.cache_data` e exceção | função que levanta, 3 reruns → executou **3** vezes (exceção não é cacheada) |

Verificado com Selenium 4.49 e Chrome 153 (*headless*) em 23/09/2026.

## Depois dos passos

```bash
cd ../demo/painel_ods_brasil
python -m src.coleta_dinamica        # ~7 s: abre o Chrome, espera, extrai, grava
streamlit run app.py                 # a página 🌳 Desmatamento lê o CSV — sem navegador
```

`saida_passo04.csv` é gerado pelo passo 4 e pode ser apagado.
