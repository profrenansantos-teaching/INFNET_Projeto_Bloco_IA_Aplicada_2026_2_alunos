"""
A ficha de um modelo do Hugging Face — lida ANTES de baixar. Painel ODS Brasil, v13 (Aula 15).

O TP4 (item 1) pede escolher o modelo por DESEMPENHO, CUSTO COMPUTACIONAL LOCAL e
ACESSIBILIDADE LOCAL. Parte disso dá para conferir sem baixar um byte, pela API do Hub:

  · ACESSIBILIDADE — o modelo é aberto ou "gated" (pede conta, aceitar a licença e um token)?
    Qual a licença? Roda com a biblioteca Transformers?
  · CUSTO — quantos parâmetros; quanto pesa o download; quanto ocupa na memória em float32
    (parâmetros × 4 bytes — a conta que a bancada confere na prática);
  · DESEMPENHO, só a PISTA — a tarefa para a qual foi treinado e as línguas que o cartão
    declara. A pista não decide: quem decide é a bancada (src/bancada.py), no nosso dado.

🐛 Tropeços reais da Aula 15 que a ficha teria evitado:
  · facebook/bart-large-mnli, o zero-shot mais baixado do Hub, não declara língua — é inglês.
    No nosso banco de provas: 9 de 30.
  · MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli é "multilingual", mas a lista do cartão
    não tem "pt". No banco de provas: 7 de 30.
  · google/gemma-3-1b-it é gated: sem conta e token, o download falha com
    OSError "You are trying to access a gated repo… 401 Client Error".
  E um que a ficha NÃO pega: o cartão do Qwen2.5 declara só "en" — e o modelo acerta 27 de 30
  em português. O cartão é pista; a medida é o veredito.

Precisa de internet (consulta o Hub). Rodar, com o ambiente de requirements-api.txt:
    python -m src.ficha_modelo Qwen/Qwen2.5-1.5B-Instruct google/gemma-3-1b-it
"""

import sys

from huggingface_hub import HfApi

BYTES_FLOAT32 = 4   # cada parâmetro, em float32, ocupa 4 bytes


def ficha(modelo: str) -> dict:
    """O que o Hub diz de um modelo — sem baixá-lo."""
    info = HfApi().model_info(modelo, files_metadata=True)
    cartao = info.card_data or {}
    # Os pesos são os .safetensors da raiz do repositório. Muitos trazem também uma cópia antiga
    # em .bin (o Transformers baixa só uma); os mais antigos, só o .bin.
    raiz = [arq for arq in info.siblings if "/" not in arq.rfilename]
    pesos = ([arq for arq in raiz if arq.rfilename.endswith(".safetensors")]
             or [arq for arq in raiz if arq.rfilename.endswith(".bin") and "training_args" not in arq.rfilename])
    parametros = info.safetensors.total if info.safetensors else None
    linguas = cartao.get("language")
    return {
        "modelo": modelo,
        "tarefa": info.pipeline_tag,
        "linguas": linguas if isinstance(linguas, list) else ([linguas] if linguas else []),
        "licenca": cartao.get("license"),
        "gated": info.gated or False,       # False, ou "auto"/"manual" quando pede acesso
        "biblioteca": info.library_name,
        "parametros": parametros,
        "download_mb": round(sum(arq.size or 0 for arq in pesos) / 1e6),
        "ram_float32_mb": round(parametros * BYTES_FLOAT32 / 1e6) if parametros else None,
        "downloads_mes": info.downloads,
    }


def alertas(f: dict) -> list[str]:
    """O que, na ficha, já desclassifica ou pede cuidado — para um painel em PORTUGUÊS, em CPU."""
    avisos = []
    if f["gated"]:
        avisos.append("gated: pede conta no Hugging Face, aceitar a licença e um token")
    if f["linguas"] and "pt" not in f["linguas"]:
        # "multilingual" sem "pt" na lista: multilíngue em quais línguas? (o MiniLM: 7 de 30)
        declaradas = [lingua for lingua in f["linguas"] if lingua != "multilingual"]
        avisos.append(f"o cartão não lista português ({', '.join(declaradas[:6])}"
                      f"{'…' if len(declaradas) > 6 else ''}) — medir antes de usar ou descartar")
    if not f["linguas"]:
        avisos.append("o cartão não declara língua — medir")
    if f["biblioteca"] != "transformers":
        avisos.append(f"biblioteca {f['biblioteca']}: não carrega com o pipeline do Transformers")
    if f["tarefa"] not in ("text-generation", "zero-shot-classification", "text-classification"):
        avisos.append(f"tarefa {f['tarefa']}: não foi treinado para classificar nem para gerar texto")
    if f["ram_float32_mb"] and f["ram_float32_mb"] > 8000:
        avisos.append(f"~{f['ram_float32_mb'] / 1000:.0f} GB em float32: não cabe num notebook de 8 GB")
    return avisos


if __name__ == "__main__":
    for nome in sys.argv[1:] or ["Qwen/Qwen2.5-1.5B-Instruct"]:
        try:
            f = ficha(nome)
        except Exception as erro:   # sem internet, nome errado, repositório removido…
            print(f"{nome}\n   não consegui ler a ficha — {type(erro).__name__}: {str(erro).splitlines()[0]}\n")
            continue
        params = f"{f['parametros'] / 1e6:,.0f} mi".replace(",", ".") if f["parametros"] else "? (o Hub não informa)"
        print(f"{nome}\n   tarefa {f['tarefa']} · licença {f['licenca']} · gated {f['gated']} · "
              f"línguas {f['linguas'] or '(não declara)'}\n   {params} de parâmetros · download {f['download_mb']} MB · "
              f"float32 na RAM ≈ {f['ram_float32_mb'] or '?'} MB · {f['downloads_mes']} downloads/mês")
        for aviso in alertas(f):
            print(f"   ⚠️  {aviso}")
        print()
