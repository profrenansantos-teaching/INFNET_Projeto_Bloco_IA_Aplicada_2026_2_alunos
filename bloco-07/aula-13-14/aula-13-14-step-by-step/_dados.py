"""
Dados dos passos das Aulas 13 e 14 — pequenos recortes REAIS (e os relatos fictícios de exemplo), em listas de
dicionários, para que os passos rodem sozinhos: sem arquivo, sem rede.

  · NOTICIAS — 3 linhas do noticias.csv da coleta da Aula 7 (Agência Brasil, CC BY 3.0 BR), como o CSV as
    grava: "publicado_em" é TEXTO, no formato dd/mm/aaaa hh:mm; "palavras" chega como texto ("431");
  · METADADOS — o que cada coleta gravou sobre si mesma (desmatamento_meta.json e coleta_meta.json da v10):
    cada um com campos diferentes;
  · DESMATAMENTO — o recorte REAL do PRODES/INPE das Aulas 11–12 (2022–2025, as 9 UFs da Amazônia Legal), o da
    Aula 14. Repare: o PRODES ainda não publicou a taxa de 2026 — e é o ano que a prefeitura pediu (o caso da v12);
  · RELATOS — 3 relatos como a API da v10 os GRAVA: com "id" e "recebido_em" (textos fictícios).

A API de verdade (o demo: a v11 e a v12) lê os arquivos inteiros. Licença dos dados do PRODES: CC BY-SA 4.0
(INPE/PRODES — TerraBrasilis). Cite e compartilhe igual.
"""

NOTICIAS = [
    {"secao": "Meio ambiente", "titulo": "Quarta-feira é de chuvas no Sudeste, Centro-Oeste e sul do Nordeste",
     "publicado_em": "02/09/2026 08:16", "palavras": "431",
     "url": "https://agenciabrasil.ebc.com.br/meio-ambiente/noticia/2026-09/quarta-feira-e-de-chuvas-no-sudeste-centro-oeste-e-sul-do-nordeste",
     "fonte": "Agência Brasil (EBC) — CC BY 3.0 BR"},
    {"secao": "Meio ambiente", "titulo": "Rio terá dia de chuva, com temperatura em declínio e mar de ressaca",
     "publicado_em": "02/09/2026 07:02", "palavras": "242",
     "url": "https://agenciabrasil.ebc.com.br/meio-ambiente/noticia/2026-09/rio-tera-dia-de-chuva-com-temperatura-em-declinio-e-mar-de-ressaca",
     "fonte": "Agência Brasil (EBC) — CC BY 3.0 BR"},
    {"secao": "Meio ambiente", "titulo": "Meteorologia prevê ciclone  extratropical com chuvas em setembro",
     "publicado_em": "01/09/2026 07:48", "palavras": "902",
     "url": "https://agenciabrasil.ebc.com.br/meio-ambiente/noticia/2026-09/meteorologia-preve-ciclone-extratropical-com-chuvas-em-setembro",
     "fonte": "Agência Brasil (EBC) — CC BY 3.0 BR"},
]

METADADOS = {
    "desmatamento": {
        "coletado_em": "01/10/2026 21:50", "site": "INPE/PRODES — TerraBrasilis",
        "url": "https://terrabrasilis.dpi.inpe.br/app/dashboard/deforestation/biomes/legal_amazon/rates",
        "licenca": "Creative Commons Atribuição-CompartilhaIgual 4.0 Internacional (CC BY-SA 4.0)",
        "ferramenta": "Selenium (Chrome sem janela) + BeautifulSoup", "origem_desta_gravacao": "navegador",
        "linhas": 342, "ufs": 9, "anos": "1988–2025", "segundos": 6.7,
    },
    "noticias": {
        "coletado_em": "02/09/2026 13:38", "site": "https://agenciabrasil.ebc.com.br",
        "licenca": "Creative Commons Atribuição 3.0 Brasil",
        "secoes": ["Meio ambiente", "Direitos humanos", "Economia"], "noticias": 15,
    },
}

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

RELATOS = [
    {"id": 1, "recebido_em": "05/10/2026 08:12", "uf": "PA", "categoria": "queimada",
     "texto": "(exemplo fictício) Fumaça densa na beira da estrada desde o começo da manhã."},
    {"id": 2, "recebido_em": "05/10/2026 10:40", "uf": "AM", "categoria": "seca",
     "texto": "(exemplo fictício) O nível do rio baixou tanto que o barco não chega mais ao porto."},
    {"id": 3, "recebido_em": "06/10/2026 07:55", "uf": "RS", "categoria": "enchente",
     "texto": "(exemplo fictício) A água do arroio subiu durante a noite e alcançou as casas."},
]
