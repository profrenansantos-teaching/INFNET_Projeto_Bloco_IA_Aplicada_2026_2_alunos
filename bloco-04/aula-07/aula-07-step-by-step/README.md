# Aula 7 — Passo a passo executável

Quatro passos numerados, cada um rodável **isoladamente**. Eles seguem a ordem real de um trabalho
de coleta — que **não** começa escrevendo código.

```bash
# na raiz do repositório, com o ambiente ativado
cd course-materials/bloco-04/aula-07/aula-07-step-by-step

python passo01_permissao.py            # posso? (acessa a rede)
python passo02_baixar_e_guardar.py     # baixa 1 página e grava o snapshot (rede)
python passo03_sopa.py                 # extrai do ARQUIVO (sem rede)
python passo04_limpar_e_gravar.py      # limpa e grava CSV (sem rede)
```

| Passo | O que ensina | Precisa de internet? |
|-------|--------------|----------------------|
| `passo01_permissao.py` | `robots.txt` com `urllib.robotparser`; `Crawl-delay`; licença; `User-Agent` honesto | **sim** |
| `passo02_baixar_e_guardar.py` | `requests.get`, **ler o status**, `raise_for_status`, gravar o snapshot | **sim** |
| `passo03_sopa.py` | `find` · `find_all` · `select` · `get_text`; `find` devolve `None`; do link ao título | **não** |
| `passo04_limpar_e_gravar.py` | `\xa0`, regex de data, guarda contra resultado vazio, `newline=""` | **não** |

> **Passos 3 e 4 rodam sempre.** O passo 3 usa o snapshot do passo 2; se ele não existir, cai num
> HTML de brinquedo embutido no próprio arquivo. Se a rede da escola cair no meio da aula, **os dois
> passos que mais ensinam continuam funcionando**.

## Se der `SSLError` (rede da escola)

O proxy da instituição intercepta TLS. É o mesmo caso da Aula 5, e a solução já está pronta — a
exceção é **configuração**, não código:

```bash
# Windows (PowerShell)
$env:PAINEL_ODS_VERIFICAR_SSL = "false"
# Linux / macOS / Git Bash
export PAINEL_ODS_VERIFICAR_SSL=false
```

O padrão continua sendo **verificar** o certificado. Só se desliga quando alguém diz explicitamente
para desligar.

## Se der `UnicodeEncodeError` no console

O terminal do Windows usa cp1252 e não imprime alguns caracteres (`→`, por exemplo). Por isso estes
scripts só imprimem caracteres que o cp1252 aceita. Se você acrescentar um `print` com seta ou
emoji, ou troque por `->`, ou rode `chcp 65001` antes.

## Arquivos gerados (e ignorados pelo Git)

| Arquivo | De onde vem | Versionado? |
|---|---|---|
| `snapshot_meio_ambiente.html` | passo 2 | **não** — HTML de terceiros, regenerável |
| `noticias_exemplo.csv` | passo 4 | não — é saída de exercício |

## Depois dos quatro passos

O que os passos fazem em pedaços, `../demo/painel_ods_brasil/src/coleta_web.py` faz de ponta a
ponta, em dois níveis (seção → matéria):

```bash
cd ../demo/painel_ods_brasil
python -m src.coleta_web --rapido    # 1 seção, 2 matérias (~30 s) — para a aula
python -m src.coleta_web             # 3 seções, 15 matérias (~186 s) — completo
python -m src.coleta_web --do-cache  # reprocessa o snapshot, sem tocar na rede
streamlit run app.py
```
