"""
A bancada de provas — mede um candidato NO NOSSO DADO, NA NOSSA MÁQUINA. Painel ODS Brasil, v13 (Aula 15).

O TP4 (item 1) pede justificar a escolha do modelo por desempenho e custo computacional. A
ficha (src/ficha_modelo.py) dá pistas; a bancada dá os NÚMEROS — os quatro que a escolha usa:

  acertos ......... no banco de provas: data/analisador/banco_de_provas.csv, 30 relatos
                    FICTÍCIOS rotulados à mão (5 por categoria; metade com as palavras que as
                    regras conhecem, metade sem elas — como o "arroio" da Aula 13)
  s por relato .... a mediana, depois de um aquecimento (o 1º pedido paga custos que os outros não pagam)
  s para carregar . do disco para a memória (o download não entra: acontece uma vez só)
  MB dos pesos .... parâmetros × bytes de cada um — o grosso da RAM que o modelo ocupa

Três motores, três jeitos de perguntar:
  regras ......... o motor da v11 (src/analisador.py) — a LINHA DE BASE: o modelo tem de bater isto
  zero-shot ...... pipeline("zero-shot-classification"): um modelo de inferência textual pergunta
                   "este relato é sobre queimada?" a cada categoria — família BERT (só encoder)
  gerar .......... pipeline("text-generation"): um LLM de conversa recebe as instruções e o relato e
                   ESCREVE a categoria — família GPT (só decoder)

🐛 Tropeço real (Aula 15): o mDeBERTa levava 5 s por relato. O Transformers 5 carrega o modelo no
   tipo em que ele foi salvo — float16 —, e a nossa CPU faz conta em float16 devagar. Com
   dtype=float32: 0,6 s, o mesmo acerto, o dobro de memória. Por isso --dtype existe (padrão:
   float32), e o resultado registra o tipo usado. (Com o bfloat16 do Qwen, a mesma história:
   metade da memória, 5 vezes mais lento — NA NOSSA CPU. Noutra, meça.)

Rodar (ambiente de requirements-api.txt; o modelo é baixado na primeira vez — o tamanho está na ficha):
    python -m src.bancada regras
    python -m src.bancada MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 --tarefa zero-shot
    python -m src.bancada Qwen/Qwen2.5-1.5B-Instruct --tarefa gerar
    python -m src.bancada Qwen/Qwen2.5-1.5B-Instruct --tarefa gerar --dtype bfloat16
    python -m src.bancada Qwen/Qwen2.5-1.5B-Instruct --tarefa gerar --prompt simples
Cada execução grava (ou atualiza) uma linha em data/analisador/avaliacao.json — é o que a página
🧪 Escolha do modelo mostra.
"""

import argparse
import csv
import json
import os
import platform
import statistics
import time
from datetime import datetime
from pathlib import Path

from src.analise_texto import _sem_acento   # a mesma normalização das regras (Aula 8)

BASE = Path(__file__).resolve().parent.parent
ARQ_BANCO = BASE / "data" / "analisador" / "banco_de_provas.csv"
ARQ_AVALIACAO = BASE / "data" / "analisador" / "avaliacao.json"
ARQ_JUSTIFICATIVA = BASE / "docs" / "escolha_do_modelo.md"

# A DECISÃO, num lugar só (Aula 15). A página 🧪 Escolha do modelo e o documento do TP4
# (docs/escolha_do_modelo.md) apontam para esta linha da avaliação; a Aula 16 põe ESTE modelo
# atrás do POST /processar_texto.
ESCOLHA = {"modelo": "Qwen/Qwen2.5-1.5B-Instruct", "tarefa": "gerar", "dtype": "float32", "prompt": "definicoes"}

# As categorias do analisador e o que cada uma quer dizer. As definições são o que o modelo
# lê: sem elas, um LLM pequeno chuta (o Qwen2.5-0.5B respondeu "Desmatamento" a 20 dos 30 relatos).
DEFINICOES = {
    "queimada": "fogo, fumaça, incêndio em mata, pasto ou plantação",
    "desmatamento": "corte ou derrubada de árvores, retirada de madeira, floresta virando pasto",
    "enchente": "água subindo, rua ou casa alagada, rio ou córrego transbordando",
    "seca": "falta de chuva, rio, açude ou poço secando, falta de água",
    "poluicao": "esgoto, óleo, produto químico, fumaça de fábrica, água ou ar contaminados",
    "lixo": "lixo, entulho, móveis ou resíduos jogados em lugar errado",
}
CATEGORIAS = list(DEFINICOES)

INSTRUCOES = {
    "definicoes": (
        "Você classifica relatos de problemas ambientais enviados por moradores de cidades brasileiras.\n"
        "Categorias:\n"
        + "".join(f"- {cat}: {definicao}\n" for cat, definicao in DEFINICOES.items())
        + "Responda apenas com o nome de UMA categoria, exatamente como escrito acima."
    ),
    "simples": (
        "Você classifica relatos de problemas ambientais enviados por moradores. "
        f"Categorias possíveis: {', '.join(CATEGORIAS)}. Responda apenas com o nome de UMA categoria, sem explicar."
    ),
}

# Para o zero-shot, cada categoria vira uma HIPÓTESE: "Este relato é sobre queimada."
ROTULOS_ZERO_SHOT = {"queimada": "queimada", "desmatamento": "desmatamento", "enchente": "enchente",
                     "seca": "seca", "poluicao": "poluição", "lixo": "lixo"}


def carregar_banco(caminho: Path = ARQ_BANCO) -> list[dict]:
    """Os relatos rotulados: [{id, categoria, texto}, ...]."""
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


def categoria_na_resposta(resposta: str) -> str | None:
    """O LLM ESCREVE — e nem sempre o que se pediu ("Desmatamento", "enchência", "Chuveiro").
    Aceita a primeira categoria que aparecer no texto; se nenhuma aparece, None."""
    normalizada = _sem_acento(resposta)
    achadas = [(normalizada.find(cat), cat) for cat in CATEGORIAS if cat in normalizada]
    return min(achadas)[1] if achadas else None


def arquitetura(config, tarefa: str) -> str:
    """Encoder, decoder ou os dois — lido da configuração do modelo, não suposto pela tarefa.
    (O BART faz zero-shot, como o mDeBERTa — mas é encoder-decoder, como o T5.)"""
    if getattr(config, "is_encoder_decoder", False):
        return "encoder-decoder"
    return "decoder" if tarefa in ("gerar", "pontuar") else "encoder"


def preparar(modelo: str, tarefa: str, dtype: str, prompt: str):
    """Carrega o motor e devolve (prever, detalhes). prever(texto) -> (categoria ou None, resposta bruta)."""
    if modelo == "regras":
        from src.analisador import MOTOR, carregar_regras, classificar

        regras = carregar_regras()
        return (lambda texto: (classificar(texto, regras)["categoria_sugerida"], "")), {
            "tarefa": "regras", "dtype": "—", "pesos_mb": 0, "motor": MOTOR,
            "arquitetura": "—"}

    import torch
    from transformers import pipeline

    tipo = "auto" if dtype == "auto" else getattr(torch, dtype)
    if tarefa == "zero-shot":
        pipe = pipeline("zero-shot-classification", model=modelo, dtype=tipo, device="cpu")
        rotulos = list(ROTULOS_ZERO_SHOT.values())
        de_volta = {rotulo: cat for cat, rotulo in ROTULOS_ZERO_SHOT.items()}

        def prever(texto):
            r = pipe(texto, candidate_labels=rotulos, hypothesis_template="Este relato é sobre {}.")
            return de_volta[r["labels"][0]], f"{r['labels'][0]} ({r['scores'][0]:.2f})"
    else:
        pipe = pipeline("text-generation", model=modelo, dtype=tipo, device="cpu")
        instrucoes = INSTRUCOES[prompt]

        def prever(texto):
            mensagens = [{"role": "system", "content": instrucoes},
                         {"role": "user", "content": f"Relato: {texto}\nCategoria:"}]
            # O modelo de conversa espera as mensagens num formato próprio (o "chat template").
            # enable_thinking=False: os Qwen3 "pensam em voz alta" antes de responder, se deixarmos;
            # os outros modelos ignoram o argumento.
            entrada = pipe.tokenizer.apply_chat_template(mensagens, tokenize=False, add_generation_prompt=True,
                                                         enable_thinking=False)
            saida = pipe(entrada, max_new_tokens=10, do_sample=False, return_full_text=False)
            resposta = saida[0]["generated_text"].strip()
            return categoria_na_resposta(resposta), resposta

    pesos = sum(p.numel() * p.element_size() for p in pipe.model.parameters())
    return prever, {"tarefa": tarefa, "dtype": str(next(pipe.model.parameters()).dtype).replace("torch.", ""),
                    "pesos_mb": round(pesos / 1e6), "motor": modelo,
                    "arquitetura": arquitetura(pipe.model.config, tarefa)}


def medir(modelo: str, tarefa: str, dtype: str = "float32", prompt: str = "definicoes") -> dict:
    banco = carregar_banco()
    inicio = time.perf_counter()
    prever, detalhes = preparar(modelo, tarefa, dtype, prompt)
    carga = time.perf_counter() - inicio

    prever(banco[0]["texto"])                       # aquecimento: não entra na conta
    tempos, erros, respostas = [], [], {}
    for relato in banco:
        relogio = time.perf_counter()
        categoria, bruta = prever(relato["texto"])
        tempos.append(time.perf_counter() - relogio)
        respostas[relato["id"]] = categoria
        if categoria != relato["categoria"]:
            erros.append({"id": relato["id"], "esperada": relato["categoria"], "sugerida": categoria, "resposta": bruta})

    return {
        "modelo": modelo,
        **detalhes,
        "prompt": prompt if detalhes["tarefa"] == "gerar" else "—",
        "acertos": len(banco) - len(erros),
        "total": len(banco),
        "sem_resposta": sum(1 for cat in respostas.values() if cat is None),
        "s_por_relato": round(statistics.median(tempos), 2),
        "s_max": round(max(tempos), 2),
        "s_carga": round(carga, 1),
        "erros": erros,
        "maquina": f"{platform.system()} {platform.release()} · {os.cpu_count()} núcleos lógicos · medido na CPU",
        "medido_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
    }


def registrar(resultado: dict, caminho: Path = ARQ_AVALIACAO) -> None:
    """Grava a medida em avaliacao.json — substituindo a anterior do MESMO arranjo (modelo, tarefa, tipo, prompt)."""
    chave = lambda r: (r["modelo"], r["tarefa"], r["dtype"], r["prompt"])   # noqa: E731
    anteriores = json.loads(caminho.read_text(encoding="utf-8")) if caminho.exists() else []
    novos = [r for r in anteriores if chave(r) != chave(resultado)] + [resultado]
    caminho.write_text(json.dumps(novos, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    args = argparse.ArgumentParser(description="Mede um motor de análise no banco de provas.")
    args.add_argument("modelo", help='"regras" ou o nome do modelo no Hub (ex.: Qwen/Qwen2.5-1.5B-Instruct)')
    args.add_argument("--tarefa", choices=["zero-shot", "gerar"], default="gerar")
    args.add_argument("--dtype", choices=["float32", "bfloat16", "float16", "auto"], default="float32",
                      help="o tipo dos números do modelo (auto = o tipo em que foi salvo)")
    args.add_argument("--prompt", choices=list(INSTRUCOES), default="definicoes")
    a = args.parse_args()

    r = medir(a.modelo, a.tarefa, a.dtype, a.prompt)
    registrar(r)
    print(f"{r['modelo']} · {r['tarefa']} · {r['dtype']} · prompt {r['prompt']}\n"
          f"   {r['acertos']} de {r['total']} certos ({r['sem_resposta']} sem resposta) · "
          f"{r['s_por_relato']} s por relato (máx. {r['s_max']}) · carga {r['s_carga']} s · pesos {r['pesos_mb']} MB")
    for e in r["erros"]:
        print(f"   #{e['id']:>2} esperada {e['esperada']:<12} sugerida {str(e['sugerida']):<12} {e['resposta']}")
    print(f"   → gravado em {ARQ_AVALIACAO.relative_to(BASE)}")
