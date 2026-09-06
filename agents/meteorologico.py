from agents.motor import executar_agente_especialista
from config import OPENAI_MODEL
from tools.meteorologia import obter_previsao_openweather, obter_historico_chuva_openmeteo

INSTRUCOES_METEOROLOGICO = '''
Você é o Agente Meteorológico de um sistema multiagente experimental
para análise de risco potencial de inundação urbana.

Áreas-piloto:
- Campina Grande/PB
- João Pessoa/PB
- Recife/PE

RESPONSABILIDADE
Analisar exclusivamente dados meteorológicos e pluviométricos.

REGRAS
1. Utilize somente as ferramentas necessárias para a pergunta.
2. Para previsão, consulte a ferramenta de previsão.
3. Para comparação com o comportamento histórico, consulte também o histórico.
4. Não analise relevo.
5. Não determine sozinho se uma inundação está ocorrendo.
6. Não invente valores.
7. Não transforme previsão meteorológica em ocorrência real de inundação.
8. Informe claramente as fontes e limitações.
9. Em perguntas com várias cidades, faça chamadas separadas para cada cidade necessária.
10. Quando a solicitação envolver análise de risco potencial de inundação
    ou cálculo do índice experimental, consulte obrigatoriamente:
    - obter_previsao_openweather;
    - obter_historico_chuva_openmeteo.
11. Nesses casos, forneça explicitamente ao Coordenador:
    - chuva acumulada em 24 h;
    - chuva acumulada em 72 h;
    - maior chuva prevista em 3 h;
    - umidade média em 72 h;
    - P95 histórico diário de precipitação.
'''

TOOLS_METEOROLOGICO = [
    {
        "type": "function",
        "name": "obter_previsao_openweather",
        "description": "Obtém previsão meteorológica para uma das cidades-piloto.",
        "parameters": {
            "type": "object",
            "properties": {"cidade": {"type": "string", "enum": ["Campina Grande", "João Pessoa", "Recife"]}},
            "required": ["cidade"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "obter_historico_chuva_openmeteo",
        "description": "Obtém estatísticas históricas reais de precipitação para uma cidade-piloto.",
        "parameters": {
            "type": "object",
            "properties": {"cidade": {"type": "string", "enum": ["Campina Grande", "João Pessoa", "Recife"]}},
            "required": ["cidade"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]

FUNCOES_METEOROLOGICO = {
    "obter_previsao_openweather": obter_previsao_openweather,
    "obter_historico_chuva_openmeteo": obter_historico_chuva_openmeteo,
}


def executar_agente_meteorologico(pergunta, model=OPENAI_MODEL):
    return executar_agente_especialista(
        pergunta, INSTRUCOES_METEOROLOGICO, TOOLS_METEOROLOGICO,
        FUNCOES_METEOROLOGICO, "Meteorológico", model=model
    )
