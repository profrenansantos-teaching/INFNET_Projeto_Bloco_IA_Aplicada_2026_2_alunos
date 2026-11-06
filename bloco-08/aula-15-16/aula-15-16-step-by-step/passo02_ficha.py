"""
Passo 2 · A ficha ANTES do download — acessibilidade e custo, pelo Hub (Aula 15 · B4)

O Hub tem centenas de milhares de modelos. Antes de baixar 3 GB, dá para saber muito pela API dele:
  · para que TAREFA o modelo foi treinado     → classificar? gerar texto? completar lacunas?
  · que LÍNGUAS o cartão declara              → tem "pt"?
  · a LICENÇA e se é GATED                    → baixa sem conta? pode usar no projeto?
  · quantos PARÂMETROS e quanto pesa          → cabe na sua máquina? (parâmetros × 4 bytes em float32)

🐛 O que a ficha mostra antes de qualquer download:
  · o mais baixado de todos os zero-shot (facebook/bart-large-mnli) não declara língua — é inglês;
  · o MiniLM "multilingual" lista 15 línguas — nenhuma é o português;
  · o Gemma é gated: sem conta e token, OSError "You are trying to access a gated repo" (401);
  · o Qwen2.5-3B é da mesma família do 1.5B, mas a licença é outra ("other", não Apache).
E o que ela NÃO mostra: o cartão do Qwen2.5 diz só "en" — e o modelo vai bem em português (passo 5).

Sem internet, o passo mostra as fichas salvas em fichas_salvas.json (27/10/2026).

Rodar:  python passo02_ficha.py
"""

import json
import sys
from pathlib import Path

CANDIDATOS = [
    "facebook/bart-large-mnli",
    "MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli",
    "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7",
    "neuralmind/bert-base-portuguese-cased",
    "Qwen/Qwen2.5-0.5B-Instruct",
    "Qwen/Qwen2.5-1.5B-Instruct",
    "Qwen/Qwen2.5-3B-Instruct",
    "google/gemma-3-1b-it",
]
SALVAS = Path(__file__).parent / "fichas_salvas.json"


def ficha(modelo: str) -> dict:
    from huggingface_hub import HfApi

    info = HfApi().model_info(modelo, files_metadata=True)
    cartao = info.card_data or {}
    raiz = [arq for arq in info.siblings if "/" not in arq.rfilename]
    pesos = ([arq for arq in raiz if arq.rfilename.endswith(".safetensors")]
             or [arq for arq in raiz if arq.rfilename.endswith(".bin") and "training_args" not in arq.rfilename])
    parametros = info.safetensors.total if info.safetensors else None
    return {
        "modelo": modelo,
        "tarefa": info.pipeline_tag,
        "linguas": cartao.get("language") or [],
        "licenca": cartao.get("license"),
        "gated": info.gated or False,
        "parametros_mi": round(parametros / 1e6) if parametros else None,
        "download_mb": round(sum(arq.size or 0 for arq in pesos) / 1e6),
        "ram_float32_mb": round(parametros * 4 / 1e6) if parametros else None,   # 4 bytes por parâmetro
    }


try:
    fichas = [ficha(m) for m in CANDIDATOS]
    if "--salvar" in sys.argv:
        SALVAS.write_text(json.dumps(fichas, ensure_ascii=False, indent=1), encoding="utf-8")
except Exception as erro:          # sem internet: as fichas salvas
    print(f"(sem acesso ao Hub — {type(erro).__name__}; mostrando as fichas salvas em 27/10/2026)\n")
    fichas = json.loads(SALVAS.read_text(encoding="utf-8"))

for f in fichas:
    linguas = f["linguas"] if isinstance(f["linguas"], list) else [f["linguas"]]
    alertas = []
    if f["gated"]:
        alertas.append("GATED: conta + licença + token")
    if "pt" not in linguas:
        alertas.append("o cartão não lista português" if linguas else "o cartão não declara língua")
    if f["tarefa"] not in ("zero-shot-classification", "text-generation"):
        alertas.append(f"tarefa {f['tarefa']}: não classifica nem conversa")
    if f["licenca"] not in ("mit", "apache-2.0"):
        alertas.append(f"licença {f['licenca']}: ler antes de usar")
    print(f"{f['modelo']}\n   {f['tarefa']} · {f['parametros_mi'] or '?'} mi de parâmetros · download {f['download_mb']} MB"
          f" · float32 na RAM ≈ {f['ram_float32_mb'] or '?'} MB · licença {f['licenca']}")
    for alerta in alertas:
        print(f"   ⚠️  {alerta}")
