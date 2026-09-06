from agents.motor import executar_agente_especialista
from config import OPENAI_MODEL
from tools.geoespacial import obter_relevo_openmeteo

INSTRUCOES_GEOESPACIAL = '''
Você é o Agente Geoespacial de um sistema multiagente experimental
para análise de risco potencial de inundação urbana.

Áreas-piloto:
- Campina Grande/PB
- João Pessoa/PB
- Recife/PE

RESPONSABILIDADE
Analisar somente as informações geoespaciais disponíveis nas ferramentas.

REGRAS
1. Utilize exclusivamente informações obtidas pelas ferramentas.
2. Atualmente, a ferramenta disponível fornece uma grade simplificada de elevação.
3. Não invente bairros, rios, canais, drenagem, uso do solo ou microtopografia.
4. Não conclua que uma área irá inundar somente por possuir menor altitude.
5. Explique as limitações da resolução espacial.
6. Em perguntas com várias cidades, faça chamadas separadas para cada cidade necessária.
'''

TOOLS_GEOESPACIAL = [
    {
        "type": "function",
        "name": "obter_relevo_openmeteo",
        "description": "Obtém informações simplificadas de elevação para uma cidade-piloto.",
        "parameters": {
            "type": "object",
            "properties": {"cidade": {"type": "string", "enum": ["Campina Grande", "João Pessoa", "Recife"]}},
            "required": ["cidade"],
            "additionalProperties": False,
        },
        "strict": True,
    }
]
FUNCOES_GEOESPACIAL = {"obter_relevo_openmeteo": obter_relevo_openmeteo}


def executar_agente_geoespacial(pergunta, model=OPENAI_MODEL):
    return executar_agente_especialista(
        pergunta, INSTRUCOES_GEOESPACIAL, TOOLS_GEOESPACIAL,
        FUNCOES_GEOESPACIAL, "Geoespacial", model=model
    )
