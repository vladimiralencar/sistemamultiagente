import json
from openai import OpenAI

from agents.meteorologico import executar_agente_meteorologico
from agents.geoespacial import executar_agente_geoespacial
from agents.analise_alertas import executar_agente_analise
from config import OPENAI_API_KEY, OPENAI_MODEL


def consultar_agente_meteorologico(pergunta: str) -> dict:
    resultado = executar_agente_meteorologico(pergunta)
    return {"agente": "Meteorológico", "resposta": resultado["resposta"], "dados_ferramentas": resultado["dados_ferramentas"], "log": resultado["log"], "rodadas": resultado["rodadas"]}


def consultar_agente_geoespacial(pergunta: str) -> dict:
    resultado = executar_agente_geoespacial(pergunta)
    return {"agente": "Geoespacial", "resposta": resultado["resposta"], "dados_ferramentas": resultado["dados_ferramentas"], "log": resultado["log"], "rodadas": resultado["rodadas"]}


def consultar_agente_analise(pergunta: str, contexto_especialistas: str) -> dict:
    resultado = executar_agente_analise(pergunta, contexto_especialistas)
    return {"agente": "Análise e Alertas", "resposta": resultado["resposta"], "dados_ferramentas": resultado["dados_ferramentas"], "log": resultado["log"], "rodadas": resultado["rodadas"]}


INSTRUCOES_COORDENADOR = '''
Você é o Agente Coordenador de um sistema multiagente experimental
para análise de risco potencial de inundação urbana.

Áreas-piloto:
- Campina Grande/PB
- João Pessoa/PB
- Recife/PE

ESPECIALISTAS DISPONÍVEIS
1. Agente Meteorológico - previsão meteorológica e histórico de precipitação.
2. Agente Geoespacial - elevação e relevo simplificado.
3. Agente de Análise e Alertas - integra dados, calcula o índice experimental e interpreta resultados e limitações.

REGRAS DE ROTEAMENTO
1. Analise primeiro a intenção da pergunta.
2. Não consulte especialistas desnecessariamente.
3. Perguntas somente sobre chuva, temperatura, umidade ou previsão: consulte o Meteorológico.
4. Perguntas somente sobre relevo ou elevação: consulte o Geoespacial.
5. Perguntas sobre risco potencial de inundação: consulte Meteorológico e Geoespacial. Ao delegar ao Meteorológico, solicite previsão, histórico e P95 histórico diário.
6. Depois de obter os resultados necessários, consulte o Agente de Análise e Alertas.
7. Ao chamar o Agente de Análise, forneça no contexto os resultados dos especialistas anteriores.
8. Para perguntas com várias cidades, delegue a comparação aos especialistas necessários.
9. Não invente informações que nenhum especialista possui.
10. Não use previsão e relevo como prova de que uma inundação está ocorrendo agora.
11. Se a pergunta exigir ocorrências em tempo real, ruas interditadas, bairros alagados, drenagem urbana, níveis de rios/canais, marés ou outros dados não disponíveis, reconheça explicitamente a limitação.
12. Se nenhuma ferramenta puder responder adequadamente, você pode responder sem chamar especialista.
13. A resposta final deve deixar claro quando um resultado é experimental.
14. Não crie um ranking geral de risco entre cidades a partir da combinação qualitativa de precipitação e relevo.
15. Quando não existir modelo integrado validado, mantenha separados os resultados pluviométricos e geoespaciais.
'''

TOOLS_COORDENADOR = [
    {"type": "function", "name": "consultar_agente_meteorologico", "description": "Delega uma tarefa meteorológica ou pluviométrica ao Agente Meteorológico.", "parameters": {"type": "object", "properties": {"pergunta": {"type": "string"}}, "required": ["pergunta"], "additionalProperties": False}, "strict": True},
    {"type": "function", "name": "consultar_agente_geoespacial", "description": "Delega uma tarefa sobre relevo ou elevação ao Agente Geoespacial.", "parameters": {"type": "object", "properties": {"pergunta": {"type": "string"}}, "required": ["pergunta"], "additionalProperties": False}, "strict": True},
    {"type": "function", "name": "consultar_agente_analise", "description": "Delega a integração e análise final ao Agente de Análise e Alertas. Use somente depois de obter os dados necessários dos especialistas.", "parameters": {"type": "object", "properties": {"pergunta": {"type": "string"}, "contexto_especialistas": {"type": "string"}}, "required": ["pergunta", "contexto_especialistas"], "additionalProperties": False}, "strict": True},
]
FUNCOES_COORDENADOR = {
    "consultar_agente_meteorologico": consultar_agente_meteorologico,
    "consultar_agente_geoespacial": consultar_agente_geoespacial,
    "consultar_agente_analise": consultar_agente_analise,
}


def executar_sistema_multiagente(pergunta: str, model: str = OPENAI_MODEL, max_rodadas: int = 8):
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY não encontrada. Configure o arquivo .env.")
    client = OpenAI(api_key=OPENAI_API_KEY)
    itens = [{"role": "user", "content": pergunta}]
    log_coordenador = []
    resultados_especialistas = []

    for rodada in range(max_rodadas):
        resposta = client.responses.create(model=model, instructions=INSTRUCOES_COORDENADOR, tools=TOOLS_COORDENADOR, tool_choice="auto", input=itens)
        itens.extend(resposta.output)
        chamadas = [item for item in resposta.output if item.type == "function_call"]
        if not chamadas:
            return {"pergunta": pergunta, "resposta": resposta.output_text, "log_coordenador": log_coordenador, "resultados_especialistas": resultados_especialistas, "rodadas_coordenador": rodada + 1}

        for chamada in chamadas:
            nome = chamada.name
            args = json.loads(chamada.arguments)
            try:
                resultado = FUNCOES_COORDENADOR[nome](**args)
                status, mensagem_erro = "ok", None
            except Exception as exc:
                resultado = {"erro": str(exc)}
                status, mensagem_erro = "erro", str(exc)
            log_coordenador.append({"rodada_coordenador": rodada + 1, "especialista_chamado": nome, "status": status, "erro": mensagem_erro})
            resultados_especialistas.append({"rodada_coordenador": rodada + 1, "especialista": nome, "resultado": resultado})
            itens.append({"type": "function_call_output", "call_id": chamada.call_id, "output": json.dumps(resultado, ensure_ascii=False, default=str)})

    raise RuntimeError("O Agente Coordenador excedeu o número máximo de rodadas.")
