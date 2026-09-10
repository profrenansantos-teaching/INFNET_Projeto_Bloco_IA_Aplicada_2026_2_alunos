# Painel de Indicadores Sustentáveis do Brasil — v3

Demo do **Projeto de Bloco: Inteligência Artificial Aplicada** (INFNET) · **Aula 5 · PB Etapa 3**.

Painel ESG/ODS com dados abertos do **IBGE**, em **Python puro** (sem pandas).
Esta versão (**v3**) é a v2 **preparada para publicação**: ambiente declarado, repositório limpo,
segredos fora do código e caminhos que sobrevivem à mudança de máquina.

## Rodar localmente

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows  ·  source .venv/bin/activate no macOS/Linux
pip install -r requirements.txt
streamlit run app.py              # abre em http://localhost:8501
```

Coleta sem interface (útil para depurar):

```bash
python -m src.data_access
```

## Publicar

Roteiro completo em **[`DEPLOY.md`](DEPLOY.md)**. Resumo: `.gitignore` → `requirements.txt` →
`git init/add/commit` → `remote add origin` → `push` → **share.streamlit.io** → *New app*
(repo · branch · `app.py`).

## Estrutura

```
painel_ods_brasil/
├── app.py                          interface (Streamlit)
├── requirements.txt                as dependências — a "receita" do ambiente
├── .gitignore                      o que NUNCA entra no repositório
├── DEPLOY.md                       roteiro de publicação
├── .streamlit/
│   ├── config.toml                 tema (identidade visual INFNET)
│   └── secrets.toml.example        modelo de segredos (o secrets.toml real é ignorado)
├── src/
│   ├── __init__.py
│   └── data_access.py              coleta via API do IBGE + fallback de cache
├── data/sample/
│   └── ufs_cache.json              cache de emergência (fallback) — versionado de propósito
└── docs/
    ├── project_charter.md          artefato TDSP (Aula 1)
    └── data_summary_report.md      artefato TDSP (Aula 1)
```

## O que mudou da v2 para a v3

| # | Mudança | Por quê |
|---|---------|---------|
| 1 | `verify=False` fixo → **`verificar_ssl()` configurável**, padrão **seguro** | um `verify=False` versionado num repositório público é vulnerabilidade; a rede da escola vira exceção declarada, não código escondido |
| 2 | Caminho do cache **ancorado em `Path(__file__)`** | caminho relativo ao diretório de execução funciona no laptop e falha no servidor |
| 3 | `requirements.txt` **completo** (`streamlit` + `requests`) | o Community Cloud instala **exatamente** o que está declarado [Richards, p183] |
| 4 | `.gitignore`, `.streamlit/config.toml`, `secrets.toml.example` | ambiente e segredos fora do repositório; tema junto do código |
| 5 | Rodapé com a **versão** | permite confirmar, olhando o app no ar, se o último `push` chegou |

## Configuração

| Chave | Onde | Padrão | Para quê |
|-------|------|--------|----------|
| `PAINEL_ODS_VERIFICAR_SSL` | variável de ambiente | `true` | desligar a verificação de TLS **apenas** em rede com proxy de inspeção |
| `verificar_ssl` | `.streamlit/secrets.toml` (ou *Edit secrets* no Community Cloud) | `true` | idem, quando rodando dentro do Streamlit |

```bash
# Exemplo (laboratório com proxy) — Windows PowerShell
$env:PAINEL_ODS_VERIFICAR_SSL = "false"; streamlit run app.py
```

## Fontes de dados

- IBGE — Localidades: `https://servicodados.ibge.gov.br/api/v1/localidades/estados`
- IBGE — Agregados (SIDRA), tabela 6579, variável 9324: população residente estimada (2025)

API pública, **sem chave**. Se estiver fora do ar, o app usa `data/sample/ufs_cache.json` e avisa a
origem na tela (*fail gracefully*).
