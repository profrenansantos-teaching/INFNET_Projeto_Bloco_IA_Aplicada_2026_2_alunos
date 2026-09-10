"""
Passo 0 — Verificador de prontidão para deploy (Painel ODS, Aula 5).

Roda ANTES de publicar e responde a uma pergunta: "este projeto sobreviveria
a sair da minha máquina?". Cada verificação corresponde a um tropeço REAL
da construção deste painel, contado na aula.

Só usa a biblioteca padrão do Python — de propósito: precisa funcionar mesmo
num ambiente onde nada foi instalado ainda.

Uso:
    python verificar_ambiente.py                 # verifica o demo desta aula
    python verificar_ambiente.py CAMINHO/DO/SEU/PROJETO

Código de saída: 0 se não houver ERRO; 1 se houver.
"""

import ast
import subprocess
import sys
from pathlib import Path

OK, AVISO, ERRO = "OK", "AVISO", "ERRO"
MARCA = {OK: "[ ok ]", AVISO: "[aviso]", ERRO: "[ERRO]"}

# Bibliotecas que vêm com o Python: não precisam estar no requirements.txt.
STDLIB = set(sys.stdlib_module_names) | {"__future__"}

resultados: list[tuple[str, str, str]] = []


def checar(nivel: str, titulo: str, detalhe: str = "") -> None:
    resultados.append((nivel, titulo, detalhe))


# --------------------------------------------------------------------------
# 1. Versão do Python
# --------------------------------------------------------------------------
def checar_python() -> None:
    v = sys.version_info
    versao = f"{v.major}.{v.minor}.{v.micro}"
    if (v.major, v.minor) >= (3, 11):
        checar(OK, f"Python {versao}", "o curso usa 3.11+")
    else:
        checar(ERRO, f"Python {versao} é antigo demais", "instale o Python 3.11 ou mais novo")


# --------------------------------------------------------------------------
# 2. Ambiente virtual ativo
# --------------------------------------------------------------------------
def checar_venv() -> None:
    dentro = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    if dentro:
        checar(OK, "Ambiente virtual ativo", Path(sys.prefix).name)
    else:
        checar(
            AVISO,
            "Você NÃO está num ambiente virtual",
            "python -m venv .venv  e depois ative — sem isso as versões de projetos diferentes brigam",
        )


# --------------------------------------------------------------------------
# 3. Arquivos que o deploy exige
# --------------------------------------------------------------------------
def checar_arquivos(proj: Path) -> None:
    for nome, nivel, dica in [
        ("app.py", ERRO, "o Community Cloud precisa de um arquivo principal para executar"),
        ("requirements.txt", ERRO, "sem ele o servidor não instala nada -> ModuleNotFoundError"),
        (".gitignore", ERRO, "sem ele o .venv/ e os segredos vão parar no repositório"),
        ("README.md", AVISO, "quem abrir o repositório precisa saber o que é e como rodar"),
    ]:
        if (proj / nome).exists():
            checar(OK, f"{nome} presente")
        else:
            checar(nivel, f"{nome} ausente", dica)


# --------------------------------------------------------------------------
# 4. requirements.txt cobre tudo que o código importa?
#    (o tropeço nº 2 visto na aula: "funciona na minha máquina")
# --------------------------------------------------------------------------
def _imports_do_projeto(proj: Path) -> set[str]:
    externos: set[str] = set()
    locais = {p.stem for p in proj.rglob("*.py")} | {
        d.name for d in proj.iterdir() if d.is_dir() and (d / "__init__.py").exists()
    }
    for arquivo in proj.rglob("*.py"):
        if any(parte in {".venv", "venv", "env", "__pycache__"} for parte in arquivo.parts):
            continue
        try:
            arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                for alias in no.names:
                    externos.add(alias.name.split(".")[0])
            elif isinstance(no, ast.ImportFrom) and no.level == 0 and no.module:
                externos.add(no.module.split(".")[0])
    return {m for m in externos if m not in STDLIB and m not in locais}


def _nomes_declarados(requirements: Path) -> set[str]:
    nomes = set()
    for linha in requirements.read_text(encoding="utf-8").splitlines():
        linha = linha.split("#")[0].strip()
        if not linha:
            continue
        for separador in ("==", ">=", "<=", "~=", ">", "<", "["):
            linha = linha.split(separador)[0]
        nomes.add(linha.strip().lower().replace("_", "-"))
    return nomes


def checar_dependencias(proj: Path) -> None:
    req = proj / "requirements.txt"
    if not req.exists():
        return
    declarados = _nomes_declarados(req)
    importados = _imports_do_projeto(proj)
    faltando = {m for m in importados if m.lower().replace("_", "-") not in declarados}
    if faltando:
        checar(
            ERRO,
            "requirements.txt incompleto",
            f"o código importa {sorted(faltando)} e o arquivo não declara — o deploy vai quebrar",
        )
    else:
        checar(OK, "requirements.txt cobre os imports", f"declarados: {sorted(declarados)}")

    # As dependências declaradas estão realmente instaladas aqui?
    import importlib.util

    ausentes = [m for m in sorted(importados) if importlib.util.find_spec(m) is None]
    if ausentes:
        checar(AVISO, "Dependências não instaladas neste ambiente", f"{ausentes} — rode pip install -r requirements.txt")


# --------------------------------------------------------------------------
# 5. .gitignore protege o essencial
# --------------------------------------------------------------------------
def checar_gitignore(proj: Path) -> None:
    gi = proj / ".gitignore"
    if not gi.exists():
        return
    texto = gi.read_text(encoding="utf-8")
    for padrao, motivo in [
        (".venv", "peso: milhares de arquivos, compilados para UM sistema operacional"),
        ("__pycache__", "peso: gerado a cada execução"),
        ("secrets.toml", "SEGURANÇA: o repositório do Community Cloud é público por padrão"),
    ]:
        if padrao in texto:
            checar(OK, f".gitignore cobre {padrao}")
        else:
            checar(ERRO, f".gitignore NÃO cobre {padrao}", motivo)


# --------------------------------------------------------------------------
# 6. Segredos
# --------------------------------------------------------------------------
def checar_segredos(proj: Path) -> None:
    if (proj / ".streamlit" / "secrets.toml.example").exists():
        checar(OK, "secrets.toml.example presente", "quem clonar sabe o que precisa preencher")
    else:
        checar(AVISO, "Sem secrets.toml.example", "versione um modelo com as chaves em branco")

    rastreados = _git(proj, "ls-files")
    if rastreados is None:
        return
    suspeitos = [
        linha
        for linha in rastreados.splitlines()
        if linha.endswith("secrets.toml") or linha == ".env" or linha.startswith(".venv/")
    ]
    if suspeitos:
        checar(
            ERRO,
            "Arquivos proibidos JÁ RASTREADOS pelo Git",
            f"{suspeitos} — .gitignore não apaga o que já entrou: use git rm -r --cached <caminho> "
            "e, se for segredo, REVOGUE a chave (o histórico guarda)",
        )
    else:
        checar(OK, "Nenhum segredo ou .venv rastreado pelo Git")


# --------------------------------------------------------------------------
# 7. Caminhos frágeis (o tropeço nº 3 visto na aula)
# --------------------------------------------------------------------------
def checar_caminhos(proj: Path) -> None:
    frageis: list[str] = []
    for arquivo in proj.rglob("*.py"):
        if any(p in {".venv", "venv", "__pycache__"} for p in arquivo.parts):
            continue
        for n, linha in enumerate(arquivo.read_text(encoding="utf-8").splitlines(), 1):
            texto = linha.strip()
            if texto.startswith("#"):
                continue
            for trecho in ('open("data/', "open('data/", 'Path("data/', "Path('data/"):
                if trecho in texto:
                    frageis.append(f"{arquivo.relative_to(proj)}:{n}")
            if "C:\\" in texto or "/Users/" in texto or "/home/" in texto:
                frageis.append(f"{arquivo.relative_to(proj)}:{n} (caminho absoluto)")
    if frageis:
        checar(
            AVISO,
            "Caminhos possivelmente frágeis",
            f"{frageis} — prefira BASE = Path(__file__).resolve().parent",
        )
    else:
        checar(OK, "Nenhum caminho frágil encontrado", "os caminhos estão ancorados em __file__")


# --------------------------------------------------------------------------
# 8. Estado do repositório
# --------------------------------------------------------------------------
def _git(proj: Path, *args: str) -> str | None:
    try:
        r = subprocess.run(
            ["git", *args], cwd=proj, capture_output=True, text=True, timeout=20
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def checar_git(proj: Path) -> None:
    raiz = _git(proj, "rev-parse", "--show-toplevel")
    if raiz is None:
        checar(AVISO, "Ainda não é um repositório Git", "git init -b main  (veja o DEPLOY.md)")
        return
    if Path(raiz).resolve() != proj:
        checar(
            AVISO,
            "O repositório Git encontrado NÃO é este projeto",
            f"a raiz do repositório é {raiz} — o Community Cloud publica a partir da raiz, "
            "então este projeto precisa do PRÓPRIO repositório",
        )
        return
    checar(OK, "Repositório Git encontrado", f"raiz: {raiz}")

    branch = _git(proj, "rev-parse", "--abbrev-ref", "HEAD")
    if branch == "main":
        checar(OK, "Branch main")
    elif branch:
        checar(AVISO, f"Branch atual: {branch}", "a convenção do curso é main (git branch -M main)")

    if _git(proj, "remote", "get-url", "origin"):
        checar(OK, "Remoto origin configurado")
    else:
        checar(AVISO, "Sem remoto origin", "git remote add origin https://github.com/USUARIO/REPO")

    pendentes = _git(proj, "status", "--porcelain")
    if pendentes:
        checar(AVISO, "Há mudanças não commitadas", "o que não está commitado NÃO está no ar")


# --------------------------------------------------------------------------
def main() -> int:
    alvo = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "demo" / "painel_ods_brasil"
    proj = alvo.resolve()

    print("=" * 74)
    print("VERIFICACAO DE PRONTIDAO PARA DEPLOY  ·  Painel ODS  ·  PB Etapa 3")
    print(f"Projeto: {proj}")
    print("=" * 74)

    if not proj.is_dir():
        print(f"{MARCA[ERRO]} Pasta nao encontrada: {proj}")
        return 1

    checar_python()
    checar_venv()
    checar_arquivos(proj)
    checar_dependencias(proj)
    checar_gitignore(proj)
    checar_segredos(proj)
    checar_caminhos(proj)
    checar_git(proj)

    for nivel, titulo, detalhe in resultados:
        print(f"{MARCA[nivel]} {titulo}")
        if detalhe:
            print(f"         -> {detalhe}")

    erros = sum(1 for n, _, _ in resultados if n == ERRO)
    avisos = sum(1 for n, _, _ in resultados if n == AVISO)
    print("-" * 74)
    print(f"Resultado: {erros} erro(s), {avisos} aviso(s), "
          f"{sum(1 for n, _, _ in resultados if n == OK)} verificacao(oes) ok")
    if erros:
        print("Corrija os ERROS antes de publicar. Veja demo/painel_ods_brasil/DEPLOY.md")
    else:
        print("Pronto para publicar. Siga o DEPLOY.md a partir do passo 3.")
    return 1 if erros else 0


if __name__ == "__main__":
    raise SystemExit(main())
