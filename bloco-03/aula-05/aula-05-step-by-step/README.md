# Aula 5 — Passo a passo: do laptop para a internet

> Cada passo é **executável e independente**. Rode um, entenda a saída, só então vá ao próximo.
> O projeto de referência é `../demo/painel_ods_brasil/` (a **v3**). Faça o mesmo no **seu** projeto.

| Passo | O que faz | Como rodar |
|------:|-----------|------------|
| **0** | Diagnostica se o projeto sobreviveria a sair da sua máquina | `python verificar_ambiente.py` |
| **1** | Recria o ambiente a partir da receita | `python -m venv .venv` → ativar → `pip install -r requirements.txt` |
| **2** | Prova que o `.gitignore` está fazendo efeito | `git status` antes e depois |
| **3** | Cria o repositório local | `git init -b main` · `git add .` · `git commit` |
| **4** | Conecta ao GitHub e envia | `git remote add origin …` · `git push -u origin main` |
| **5** | Publica no Streamlit Community Cloud | share.streamlit.io → New app |
| **6** | Atualiza o app publicado | editar → `commit` → `push` → recarregar a URL |

---

## Passo 0 · Diagnóstico (`verificar_ambiente.py`)

```bash
python verificar_ambiente.py                     # verifica o demo desta aula
python verificar_ambiente.py ../../../meu_projeto   # verifica o SEU projeto
```

Verifica, em ordem: versão do Python · ambiente virtual ativo · arquivos exigidos pelo deploy ·
**se o `requirements.txt` cobre tudo que o código importa** · `.gitignore` · segredos rastreados ·
caminhos frágeis · estado do repositório.

Sai com código **1** se houver ERRO e **0** se estiver pronto. Cada verificação corresponde a um
tropeço real da construção deste painel, contado na aula.

> **Exemplo real (aconteceu na preparação deste material):** o script apontou
> `requirements.txt incompleto: o código importa ['urllib3']`. O `urllib3` chega junto com o
> `requests`, mas `src/data_access.py` o importa **diretamente** — e o que se importa, se declara.
> Depender da dependência de outra biblioteca é apostar que ela nunca vai mudar.

## Passo 1 · Ambiente reprodutível

```bash
cd ../demo/painel_ods_brasil
python -m venv .venv

.venv\Scripts\Activate.ps1        # Windows (PowerShell)
source .venv/bin/activate         # macOS / Linux

pip install -r requirements.txt
streamlit run app.py              # confirme que roda ANTES de publicar
```

**Teste mental do passo:** *se eu apagar `.venv/` agora, consigo reconstruir?* Se a resposta for não,
falta alguma coisa no `requirements.txt`.

## Passo 2 · O `.gitignore` em ação

```bash
git status --short | wc -l        # com .gitignore
mv .gitignore .gitignore.off
git status --short | wc -l        # sem .gitignore  (agora conte de novo)
mv .gitignore.off .gitignore
```

A diferença entre alguns arquivos e alguns milhares é o argumento inteiro.
**`.venv/` não é versionado porque é reconstruível** — e porque contém binários compilados para *um*
sistema operacional, inúteis no servidor.

> ⚠️ `.gitignore` **não** remove o que já está rastreado. Se o `.venv/` já entrou:
> `git rm -r --cached .venv` e commit.

## Passo 3 · Repositório local

```bash
git init -b main
git status                        # NÃO pode aparecer .venv/ nem .streamlit/secrets.toml
git add .
git commit -m "Painel ODS v3: projeto pronto para publicação"
```

`main` (não `master`) é a convenção do curso — e o padrão do GitHub.

## Passo 4 · Enviar para o GitHub

No site: **New repository** → nome `painel-ods-brasil` → **Create repository**.

```bash
git remote add origin https://github.com/SEU_USUARIO/painel-ods-brasil
git push -u origin main
```

`origin` = apelido da URL remota. `-u` grava o vínculo; dali em diante basta `git push`.

## Passo 5 · Publicar

1. **share.streamlit.io** → entrar com o GitHub.
2. **New app** → **repositório** · **branch** (`main`) · **arquivo principal** (`app.py`).
3. **Deploy** → o serviço instala o `requirements.txt`, executa o `app.py` e devolve **uma URL**.

Se quebrar: **Manage app** → logs. As três mensagens mais comuns e o que fazer estão na tabela do
`../demo/painel_ods_brasil/DEPLOY.md`, seção 6.

## Passo 6 · O ciclo que muda o hábito

```bash
# edite o app.py (ex.: mude a constante VERSAO ou o st.title)
git add .
git commit -m "novo título do painel"
git push
```

Recarregue a URL. Leva um ou dois minutos. **O rodapé do app mostra a `VERSAO`** — é assim que você
confirma, olhando a página publicada, que o `push` chegou lá.

> **A frase para levar:** o `git push` **é** o botão de publicar. Se não está commitado, não está no ar.

---

## Erros que você provavelmente vai encontrar

| Sintoma | Causa | Correção |
|---------|-------|----------|
| `ModuleNotFoundError` no log do deploy | dependência não declarada | acrescentar ao `requirements.txt` → `push` |
| `FileNotFoundError` só no ar | caminho relativo ao diretório de execução | `BASE = Path(__file__).resolve().parent` |
| `push` rejeitado (`Updates were rejected`) | o remoto tem commits que você não tem | `git pull --rebase` e depois `git push` |
| Deploy pede autorização de repositório privado | repositório não é público | tornar público ou autorizar o acesso na conta |
| O app no ar mostra "cache local" | a API do IBGE não respondeu | é o *fallback* funcionando — comportamento esperado |
| Erro de certificado (`SSLError`) na rede da escola | proxy com inspeção de TLS | `PAINEL_ODS_VERIFICAR_SSL=false` **só localmente** — nunca no repositório |
