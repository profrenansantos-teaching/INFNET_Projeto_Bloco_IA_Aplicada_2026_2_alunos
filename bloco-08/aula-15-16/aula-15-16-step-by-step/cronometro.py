"""
O cronômetro dos passos da Aula 16 — um cliente que mede quanto cada pedido leva. (Não é um passo.)

Suba o passo num terminal (ex.: uvicorn passo01_por_requisicao:app) e, noutro:

    python cronometro.py analisar 3     três análises seguidas: quanto levou cada uma?
    python cronometro.py junto          a análise de um relato LONGO e, no meio dela, um GET /saude: quanto ele esperou?
"""

import sys
import threading
import time

import requests

URL = "http://127.0.0.1:8000"
RELATO = "A água do arroio subiu durante a noite e alcançou as casas da rua de baixo."
# O pior caso que o contrato aceita: perto dos 2.000 caracteres. Mais texto, mais conta — e mais tempo
# com o modelo ocupado (é o que deixa o bloqueio do passo 3 à vista).
RELATO_LONGO = " ".join([RELATO] * 25)


def analisar(texto: str = RELATO) -> float:
    relogio = time.perf_counter()
    r = requests.post(f"{URL}/processar_texto", json={"texto": texto}, timeout=120)
    segundos = time.perf_counter() - relogio
    print(f"   POST /processar_texto ({len(texto)} caracteres) → {r.status_code} em {segundos:.1f} s · {r.text[:90]}")
    return segundos


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "analisar"
    if modo == "analisar":
        for _ in range(int(sys.argv[2]) if len(sys.argv) > 2 else 3):
            analisar()
    else:
        # A análise de um relato LONGO numa thread; 0,5 s depois, o /saude — que não tem nada a ver com o modelo.
        analise = threading.Thread(target=analisar, args=(RELATO_LONGO,))
        analise.start()
        time.sleep(0.5)
        relogio = time.perf_counter()
        r = requests.get(f"{URL}/saude", timeout=120)
        print(f"   GET /saude (pedido no meio da análise) → {r.status_code} em {time.perf_counter() - relogio:.2f} s")
        analise.join()
