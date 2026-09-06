from agents.motor import executar_agente_especialista
from config import OPENAI_MODEL
from core.ieap import calcular_indice_atencao

INSTRUCOES_ANALISE = '''
Você é o Agente de Análise de Risco e Alertas de um sistema multiagente experimental.

RESPONSABILIDADE
Integrar dados produzidos pelos outros agentes e, quando os valores necessários
estiverem disponíveis, utilizar a ferramenta de cálculo do índice experimental.

REGRAS
1. Utilize exclusivamente o contexto fornecido e a ferramenta disponível.
2. Não invente valores ausentes.
3. Para calcular o índice, copie EXATAMENTE os valores fornecidos pelo Agente Meteorológico.
4. Não altere unidades.
5. O índice é experimental e não é previsão hidrológica validada.
6. Nunca afirme que haverá inundação.
7. Use expressões como: nível experimental de atenção; atenção pluviométrica; risco potencial; condições meteorológicas.
8. Diferencie dados meteorológicos, históricos, geoespaciais e alertas oficiais.
9. Não identifique bairros ou ruas alagadas sem dados específicos.
10. Explique as limitações dos dados.
11. Se não houver dados suficientes para o cálculo, não invente argumentos para a ferramenta.
12. Não produza um ranking geral de risco de inundação combinando qualitativamente o índice pluviométrico com elevação.
13. O índice experimental atualmente representa apenas atenção pluviométrica e não incorpora relevo em sua fórmula.
14. Em comparações entre cidades, apresente separadamente: atenção pluviométrica experimental; características do relevo.
15. Somente combine esses componentes em um único índice ou ranking se existir uma função explícita e validada para essa integração.
'''

TOOLS_ANALISE = [
    {
        "type": "function",
        "name": "calcular_indice_atencao",
        "description": "Calcula índice experimental de atenção pluviométrica a partir de dados já obtidos.",
        "parameters": {
            "type": "object",
            "properties": {
                "chuva_24h_mm": {"type": "number"},
                "chuva_72h_mm": {"type": "number"},
                "maior_chuva_3h_mm": {"type": "number"},
                "umidade_media_72h_pct": {"type": "number"},
                "p95_historico_diario_mm": {"type": "number"},
            },
            "required": ["chuva_24h_mm", "chuva_72h_mm", "maior_chuva_3h_mm", "umidade_media_72h_pct", "p95_historico_diario_mm"],
            "additionalProperties": False,
        },
        "strict": True,
    }
]
FUNCOES_ANALISE = {"calcular_indice_atencao": calcular_indice_atencao}


def executar_agente_analise(pergunta, contexto_especialistas, model=OPENAI_MODEL):
    entrada = f'''PERGUNTA ORIGINAL:\n{pergunta}\n\nDADOS PRODUZIDOS PELOS AGENTES ESPECIALISTAS:\n{contexto_especialistas}\n\nProduza a análise solicitada.'''
    return executar_agente_especialista(
        entrada, INSTRUCOES_ANALISE, TOOLS_ANALISE, FUNCOES_ANALISE,
        "Análise e Alertas", model=model
    )
