"""
Dados dos passos da Aula 11 — um recorte REAL do PRODES/INPE (2022–2025, as 9 UFs da Amazônia Legal).

Tirado do CSV que a coleta da Aula 10 gravou (`../demo/painel_ods_brasil/data/processed/
desmatamento_prodes.csv`, coleta de 01/10/2026). Fica aqui, numa lista de dicionários, para que os
passos rodem sozinhos — sem depender de arquivo nem de rede. A API de verdade (passo 5, a v9) lê o
CSV inteiro.

Licença dos dados: CC BY-SA 4.0 (INPE/PRODES — TerraBrasilis). Cite e compartilhe igual.
"""

LICENCA = "CC BY-SA 4.0 — INPE/PRODES (TerraBrasilis)"

DESMATAMENTO = [
    {"uf": "AC", "estado": "Acre", "ano": 2022, "area_km2": 840.0},
    {"uf": "AM", "estado": "Amazonas", "ano": 2022, "area_km2": 2594.0},
    {"uf": "AP", "estado": "Amapá", "ano": 2022, "area_km2": 14.0},
    {"uf": "MA", "estado": "Maranhão", "ano": 2022, "area_km2": 271.0},
    {"uf": "MT", "estado": "Mato Grosso", "ano": 2022, "area_km2": 1927.0},
    {"uf": "PA", "estado": "Pará", "ano": 2022, "area_km2": 4162.0},
    {"uf": "RO", "estado": "Rondônia", "ano": 2022, "area_km2": 1480.0},
    {"uf": "RR", "estado": "Roraima", "ano": 2022, "area_km2": 279.0},
    {"uf": "TO", "estado": "Tocantins", "ano": 2022, "area_km2": 27.0},
    {"uf": "AC", "estado": "Acre", "ano": 2023, "area_km2": 601.0},
    {"uf": "AM", "estado": "Amazonas", "ano": 2023, "area_km2": 1610.0},
    {"uf": "AP", "estado": "Amapá", "ano": 2023, "area_km2": 17.0},
    {"uf": "MA", "estado": "Maranhão", "ano": 2023, "area_km2": 306.0},
    {"uf": "MT", "estado": "Mato Grosso", "ano": 2023, "area_km2": 2048.0},
    {"uf": "PA", "estado": "Pará", "ano": 2023, "area_km2": 3299.0},
    {"uf": "RO", "estado": "Rondônia", "ano": 2023, "area_km2": 867.0},
    {"uf": "RR", "estado": "Roraima", "ano": 2023, "area_km2": 284.0},
    {"uf": "TO", "estado": "Tocantins", "ano": 2023, "area_km2": 32.0},
    {"uf": "AC", "estado": "Acre", "ano": 2024, "area_km2": 449.0},
    {"uf": "AM", "estado": "Amazonas", "ano": 2024, "area_km2": 1223.0},
    {"uf": "AP", "estado": "Amapá", "ano": 2024, "area_km2": 27.0},
    {"uf": "MA", "estado": "Maranhão", "ano": 2024, "area_km2": 307.0},
    {"uf": "MT", "estado": "Mato Grosso", "ano": 2024, "area_km2": 1257.0},
    {"uf": "PA", "estado": "Pará", "ano": 2024, "area_km2": 2395.0},
    {"uf": "RO", "estado": "Rondônia", "ano": 2024, "area_km2": 360.0},
    {"uf": "RR", "estado": "Roraima", "ano": 2024, "area_km2": 468.0},
    {"uf": "TO", "estado": "Tocantins", "ano": 2024, "area_km2": 32.0},
    {"uf": "AC", "estado": "Acre", "ano": 2025, "area_km2": 324.0},
    {"uf": "AM", "estado": "Amazonas", "ano": 2025, "area_km2": 979.0},
    {"uf": "AP", "estado": "Amapá", "ano": 2025, "area_km2": 17.0},
    {"uf": "MA", "estado": "Maranhão", "ano": 2025, "area_km2": 210.0},
    {"uf": "MT", "estado": "Mato Grosso", "ano": 2025, "area_km2": 1593.0},
    {"uf": "PA", "estado": "Pará", "ano": 2025, "area_km2": 2064.0},
    {"uf": "RO", "estado": "Rondônia", "ano": 2025, "area_km2": 229.0},
    {"uf": "RR", "estado": "Roraima", "ano": 2025, "area_km2": 285.0},
    {"uf": "TO", "estado": "Tocantins", "ano": 2025, "area_km2": 30.0},
]
