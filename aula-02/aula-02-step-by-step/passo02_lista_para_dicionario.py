"""
PASSO 2 — Lista → Dicionário por_id (§3.1 + tratamento de tipos)
Corresponde a: montar por_id para casar UFs com os dados de população depois.

Problema real: o id das UFs vem COMO TEXTO na API de Agregados.
Aqui já preparamos tudo com int(...) para evitar erro de chave depois.

Rode:  python passo02_lista_para_dicionario.py
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import json
from pathlib import Path

DADOS = Path(__file__).resolve().parent / "dados"

ufs = json.loads((DADOS / "passo01_ufs_resposta_bruta.json").read_text(encoding="utf-8"))

print("=" * 60)
print("PASSO 2: Lista de UFs -> Dicionario por_id (busca rapida)")
print("=" * 60)
print(f"Entrada: {len(ufs)} UFs na lista (vindas do Passo 1)")

por_id = {}
for e in ufs:
    chave = int(e["id"])
    por_id[chave] = {
        "uf": e["sigla"],
        "estado": e["nome"],
        "regiao": e["regiao"]["nome"],
    }

print(f"\n[OK] Dicionario montado com {len(por_id)} chaves.")

print("\n[INFO] Buscando 3 UFs por id (busca rapida O(1) no dicionario):")
for id_teste in [35, 33, 11]:
    dado = por_id[id_teste]
    print(f"   id={id_teste:>2} -> UF={dado['uf']}, Estado={dado['estado']}, Regiao={dado['regiao']}")

ARQ_SAIDA = DADOS / "passo02_ufs_por_id.json"
ARQ_SAIDA.write_text(json.dumps(por_id, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\n[SALVO] Dicionario salvo em: {ARQ_SAIDA.name}")

print("\nPASSO 2 OK! Agora temos por_id{...} para cruzar com a populacao.")
print("   Proximo passo (3): chamar API de Agregados e NAVEGAR o JSON aninhado.")
