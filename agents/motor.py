import json
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL


def _client():
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY não encontrada. Configure o arquivo .env.")
    return OpenAI(api_key=OPENAI_API_KEY)


def executar_agente_especialista(
    pergunta,
    instructions,
    tools,
    funcoes,
    nome_agente,
    model=OPENAI_MODEL,
    max_rodadas=6,
):
    client = _client()
    itens = [{"role": "user", "content": pergunta}]
    log = []
    dados_ferramentas = []

    for rodada in range(max_rodadas):
        resposta = client.responses.create(
            model=model,
            instructions=instructions,
            tools=tools,
            tool_choice="auto",
            input=itens,
        )
        itens.extend(resposta.output)
        chamadas = [item for item in resposta.output if item.type == "function_call"]

        if not chamadas:
            return {
                "agente": nome_agente,
                "resposta": resposta.output_text,
                "log": log,
                "dados_ferramentas": dados_ferramentas,
                "rodadas": rodada + 1,
            }

        for chamada in chamadas:
            nome = chamada.name
            args = json.loads(chamada.arguments)
            try:
                resultado = funcoes[nome](**args)
                status = "ok"
            except Exception as exc:
                resultado = {"erro": str(exc)}
                status = "erro"

            log.append(
                {
                    "agente": nome_agente,
                    "rodada": rodada + 1,
                    "ferramenta": nome,
                    "argumentos": args,
                    "status": status,
                }
            )
            dados_ferramentas.append(
                {"ferramenta": nome, "argumentos": args, "resultado": resultado}
            )
            itens.append(
                {
                    "type": "function_call_output",
                    "call_id": chamada.call_id,
                    "output": json.dumps(resultado, ensure_ascii=False, default=str),
                }
            )

    raise RuntimeError(f"{nome_agente} excedeu o número máximo de rodadas.")
