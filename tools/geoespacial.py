import numpy as np
import requests

from config import CIDADES


def _grade_3x3(lat: float, lon: float, deslocamento: float = 0.035):
    return [
        (lat + dlat, lon + dlon)
        for dlat in [-deslocamento, 0.0, deslocamento]
        for dlon in [-deslocamento, 0.0, deslocamento]
    ]


def obter_relevo_openmeteo(cidade: str) -> dict:
    if cidade not in CIDADES:
        raise ValueError(f"Cidade não suportada: {cidade}")

    cfg = CIDADES[cidade]
    pontos = _grade_3x3(cfg["lat"], cfg["lon"])
    latitudes = ",".join(str(p[0]) for p in pontos)
    longitudes = ",".join(str(p[1]) for p in pontos)

    url = "https://api.open-meteo.com/v1/elevation"
    params = {"latitude": latitudes, "longitude": longitudes}

    resposta = requests.get(url, params=params, timeout=30)
    resposta.raise_for_status()
    dados = resposta.json()
    elevacoes = dados.get("elevation", [])
    if not elevacoes:
        raise RuntimeError("Não foram retornados dados de elevação.")

    elevacoes = [float(x) for x in elevacoes]
    return {
        "cidade": cidade,
        "uf": cfg["uf"],
        "fonte": "Open-Meteo Elevation API / Copernicus DEM GLO-90",
        "numero_pontos": len(elevacoes),
        "elevacao_min_m": round(min(elevacoes), 1),
        "elevacao_media_m": round(float(np.mean(elevacoes)), 1),
        "elevacao_max_m": round(max(elevacoes), 1),
        "amplitude_m": round(max(elevacoes) - min(elevacoes), 1),
        "pontos": [
            {
                "latitude": round(lat, 5),
                "longitude": round(lon, 5),
                "elevacao_m": elev,
            }
            for (lat, lon), elev in zip(pontos, elevacoes)
        ],
    }
