import os
from dotenv import load_dotenv

load_dotenv()

CIDADES = {
    "Campina Grande": {"uf": "PB", "lat": -7.2306, "lon": -35.8811},
    "João Pessoa": {"uf": "PB", "lat": -7.1150, "lon": -34.8631},
    "Recife": {"uf": "PE", "lat": -8.0476, "lon": -34.8770},
}

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna").strip()

HISTORICO_INICIO = os.getenv("HISTORICO_INICIO", "2024-01-01")
HISTORICO_FIM = os.getenv("HISTORICO_FIM", "2025-12-31")
