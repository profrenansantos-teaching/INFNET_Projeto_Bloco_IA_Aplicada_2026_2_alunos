"""
PASSO 1 — Chamada BÁSICA à API do IBGE (§3.1 das notas)
Corresponde a: requests.get → raise_for_status → .json()

Objetivo: ver que a API retorna uma LISTA de dicionários (JSON semi-estruturado).
Cada item é uma UF com id, sigla, nome, região (aninhada!).

Rode:  python passo01_chamada_basica.py
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import json
import os
from pathlib import Path

import requests

try:
    import urllib3
    urllib3.disable_warnings()
except Exception:
    pass

URL_ESTADOS = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
UA = {"User-Agent": "INFNET-PB-demo/1.0"}
ARQUIVO_SALVO = Path(__file__).resolve().parent / "dados" / "passo01_ufs_resposta_bruta.json"

print("=" * 60)
print("PASSO 1: Chamada BÁSICA à API de Localidades do IBGE")
print("=" * 60)

if sys.stdin.isatty():
    modo = input("Usar (1) API ao vivo ou (2) arquivo salvo? [1/2] (padrão: 2): ").strip()
else:
    modo = ""
if modo == "":
    modo = "2"

if modo == "1":
    print("\n[API] Fazendo GET para a API...")
    resp = requests.get(
        URL_ESTADOS,
        params={"orderBy": "nome"},
        headers=UA,
        timeout=30,
        verify=False,
    )
    print(f"   Status HTTP: {resp.status_code}")
    resp.raise_for_status()
    ufs = resp.json()
else:
    print(f"\n[ARQUIVO] Carregando do arquivo salvo: {ARQUIVO_SALVO.name}")
    ufs = json.loads(ARQUIVO_SALVO.read_text(encoding="utf-8"))

print(f"\n[INFO] Tipo do dado retornado: {type(ufs).__name__} com {len(ufs)} itens")

print("\n[INFO] Primeira UF (INDICE 0) - estrutura COMPLETA:")
primeira = ufs[0]
print(json.dumps(primeira, indent=2, ensure_ascii=False))

print("\n[INFO] Campos que podemos acessar diretamente:")
print(f"   primeira['id']    = {primeira['id']}       (tipo: {type(primeira['id']).__name__})")
print(f"   primeira['sigla'] = {primeira['sigla']}")
print(f"   primeira['nome']  = {primeira['nome']}")
print(f"   primeira['regiao']= {primeira['regiao']}  <- E OUTRO dicionario aninhado!")

print("\n[INFO] Acessando a regiao aninhada:")
print(f"   primeira['regiao']['nome']  = {primeira['regiao']['nome']}")
print(f"   primeira['regiao']['sigla'] = {primeira['regiao']['sigla']}")

print("\nPASSO 1 OK! Temos 27 UFs, cada uma com id (numero), sigla, nome e regiao aninhada.")
print("   Proximo passo (2): transformar essa LISTA em um DICIONARIO por id -> busca rapida.")

