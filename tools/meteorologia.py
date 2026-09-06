import requests
import pandas as pd

from config import CIDADES, OPENWEATHER_API_KEY, HISTORICO_INICIO, HISTORICO_FIM


def obter_previsao_openweather(cidade: str) -> dict:
    if cidade not in CIDADES:
        raise ValueError(f"Cidade não suportada: {cidade}")
    if not OPENWEATHER_API_KEY:
        raise ValueError("OPENWEATHER_API_KEY não encontrada. Configure o arquivo .env.")

    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": CIDADES[cidade]["lat"],
        "lon": CIDADES[cidade]["lon"],
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "pt_br",
    }

    resposta = requests.get(url, params=params, timeout=30)
    resposta.raise_for_status()
    dados = resposta.json()

    registros = []
    for item in dados.get("list", []):
        chuva_3h = item.get("rain", {}).get("3h", 0.0)
        registros.append(
            {
                "data_hora": item["dt_txt"],
                "chuva_3h_mm": float(chuva_3h),
                "temperatura_c": float(item["main"]["temp"]),
                "umidade_pct": float(item["main"]["humidity"]),
                "vento_ms": float(item["wind"]["speed"]),
                "descricao": item["weather"][0]["description"],
            }
        )

    if not registros:
        raise RuntimeError("A API não retornou registros de previsão.")

    df = pd.DataFrame(registros)
    df["data_hora"] = pd.to_datetime(df["data_hora"])
    primeiras_24h = df.iloc[:8]
    primeiras_72h = df.iloc[:24]

    return {
        "cidade": cidade,
        "uf": CIDADES[cidade]["uf"],
        "fonte": "OpenWeatherMap - 5 Day / 3 Hour Forecast",
        "chuva_24h_mm": round(float(primeiras_24h["chuva_3h_mm"].sum()), 2),
        "chuva_72h_mm": round(float(primeiras_72h["chuva_3h_mm"].sum()), 2),
        "maior_chuva_3h_mm": round(float(primeiras_72h["chuva_3h_mm"].max()), 2),
        "umidade_media_72h_pct": round(float(primeiras_72h["umidade_pct"].mean()), 1),
        "vento_max_72h_ms": round(float(primeiras_72h["vento_ms"].max()), 1),
        "numero_intervalos_72h": int(len(primeiras_72h)),
        "primeiros_intervalos": primeiras_24h.to_dict(orient="records"),
    }


def obter_historico_chuva_openmeteo(
    cidade: str,
    inicio: str = HISTORICO_INICIO,
    fim: str = HISTORICO_FIM,
) -> dict:
    if cidade not in CIDADES:
        raise ValueError(f"Cidade não suportada: {cidade}")

    cfg = CIDADES[cidade]
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": cfg["lat"],
        "longitude": cfg["lon"],
        "start_date": inicio,
        "end_date": fim,
        "daily": "precipitation_sum",
        "timezone": "America/Fortaleza",
    }

    resposta = requests.get(url, params=params, timeout=60)
    resposta.raise_for_status()
    dados = resposta.json()

    chuva = dados.get("daily", {}).get("precipitation_sum", [])
    serie = pd.Series(chuva, dtype="float64").dropna()
    if serie.empty:
        raise RuntimeError("Não foram obtidos dados históricos de precipitação.")

    return {
        "cidade": cidade,
        "uf": cfg["uf"],
        "fonte": "Open-Meteo Historical Weather API",
        "periodo_inicio": inicio,
        "periodo_fim": fim,
        "n_dias": int(len(serie)),
        "media_diaria_mm": round(float(serie.mean()), 2),
        "maximo_diario_mm": round(float(serie.max()), 2),
        "p75_diario_mm": round(float(serie.quantile(0.75)), 2),
        "p90_diario_mm": round(float(serie.quantile(0.90)), 2),
        "p95_diario_mm": round(float(serie.quantile(0.95)), 2),
        "p99_diario_mm": round(float(serie.quantile(0.99)), 2),
    }
