from datetime import datetime

from config import CIDADES
from core.ieap import calcular_indice_atencao
from tools.meteorologia import obter_previsao_openweather, obter_historico_chuva_openmeteo
from tools.geoespacial import obter_relevo_openmeteo


def _contribuicoes_ieap(previsao: dict, historico: dict) -> dict:
    """Decompõe o IEAP exatamente com os mesmos termos do notebook v06.

    A função não altera o cálculo oficial; serve apenas para explicabilidade no dashboard.
    """
    p95 = max(float(historico["p95_diario_mm"]), 1.0)
    chuva_24h = float(previsao["chuva_24h_mm"])
    chuva_72h = float(previsao["chuva_72h_mm"])
    chuva_3h = float(previsao["maior_chuva_3h_mm"])
    umidade = float(previsao["umidade_media_72h_pct"])

    r24 = chuva_24h / p95
    r72 = chuva_72h / (2.0 * p95)

    c24 = min(r24, 1.5) / 1.5 * 45
    c72 = min(r72, 1.5) / 1.5 * 30
    c3h = min(chuva_3h / 30.0, 1.0) * 20
    chum = max(0.0, min((umidade - 70.0) / 25.0, 1.0)) * 5

    return {
        "chuva_24h": round(c24, 2),
        "chuva_72h": round(c72, 2),
        "chuva_3h": round(c3h, 2),
        "umidade": round(chum, 2),
    }


def _comparacao(valor: float, referencia: float) -> str:
    if referencia <= 0:
        return "sem referência histórica válida para comparação"
    razao = valor / referencia
    if razao < 0.5:
        return "bem abaixo da referência histórica utilizada"
    if razao < 1.0:
        return "abaixo da referência histórica utilizada"
    if razao < 1.25:
        return "próxima ou ligeiramente acima da referência histórica utilizada"
    return "acima da referência histórica utilizada"


def _gerar_analise_multiagente(cidade: str, previsao: dict, historico: dict, relevo: dict, indice: dict) -> dict:
    """Gera uma síntese rica, explicável e determinística para o dashboard.

    A redação segue as limitações metodológicas do notebook v06: IEAP e relevo
    permanecem separados, e o sistema não afirma ocorrência de inundação.
    """
    score = float(indice["score_0_100"])
    nivel = indice["nivel_atencao"].lower()
    p95 = float(historico["p95_diario_mm"])
    chuva24 = float(previsao["chuva_24h_mm"])
    chuva72 = float(previsao["chuva_72h_mm"])
    chuva3 = float(previsao["maior_chuva_3h_mm"])
    umidade = float(previsao["umidade_media_72h_pct"])

    contrib = _contribuicoes_ieap(previsao, historico)
    rotulos = {
        "chuva_24h": "chuva prevista em 24 horas",
        "chuva_72h": "chuva acumulada prevista em 72 horas",
        "chuva_3h": "maior acumulado previsto em 3 horas",
        "umidade": "umidade média prevista em 72 horas",
    }
    dominante = max(contrib, key=contrib.get)
    pontos_dom = contrib[dominante]

    meteorologico = (
        f"Para {cidade}, o Agente Meteorológico identificou {chuva24:.1f} mm de chuva prevista em 24 horas, "
        f"{chuva72:.1f} mm em 72 horas e maior acumulado de {chuva3:.1f} mm em uma janela de 3 horas. "
        f"A umidade média prevista é {umidade:.1f}%. O P95 diário histórico utilizado como referência é "
        f"{p95:.1f} mm. O acumulado de 24 horas está {_comparacao(chuva24, p95)}, enquanto o acumulado de "
        f"72 horas é comparado pelo modelo com 2×P95 ({2*p95:.1f} mm) e está {_comparacao(chuva72, 2*p95)}."
    )

    geoespacial = (
        f"O Agente Geoespacial analisou uma grade simplificada de elevação. Para {cidade}, a elevação média "
        f"é {relevo['elevacao_media_m']:.1f} m, variando de {relevo['elevacao_min_m']:.1f} m a "
        f"{relevo['elevacao_max_m']:.1f} m, com amplitude altimétrica de {relevo['amplitude_m']:.1f} m. "
        "Essas informações descrevem o relevo de forma complementar; não são combinadas com a precipitação "
        "para formar o IEAP e, isoladamente, não permitem afirmar onde ocorrerá inundação."
    )

    if pontos_dom > 0:
        explicacao_dom = (
            f"A maior contribuição individual para o índice veio da {rotulos[dominante]}, "
            f"com aproximadamente {pontos_dom:.1f} pontos na composição do IEAP."
        )
    else:
        explicacao_dom = "Nenhum componente meteorológico acrescentou contribuição relevante ao índice nesta execução."

    analise_alertas = (
        f"O Agente de Análise e Alertas calculou IEAP de {score:.1f}, classificado como {nivel} atenção "
        f"pluviométrica experimental. {explicacao_dom} A leitura deve ser feita como indicador de atenção "
        "pluviométrica, e não como probabilidade validada de inundação."
    )

    if score < 25:
        sintese_nivel = "os dados disponíveis não indicam, no período analisado, condições pluviométricas de elevada atenção"
    elif score < 50:
        sintese_nivel = "os dados disponíveis indicam atenção pluviométrica moderada e justificam acompanhamento das próximas atualizações"
    elif score < 75:
        sintese_nivel = "os dados disponíveis indicam atenção pluviométrica elevada e recomendam acompanhamento mais próximo das atualizações meteorológicas e dos canais oficiais"
    else:
        sintese_nivel = "os dados disponíveis indicam atenção pluviométrica muito elevada e reforçam a importância de acompanhar continuamente as atualizações meteorológicas e os canais oficiais"

    coordenador = (
        f"Na síntese do Agente Coordenador, {sintese_nivel}. "
        f"O IEAP calculado para {cidade} é {score:.1f}, classificado como {nivel} atenção pluviométrica, "
        "e a síntese integra os resultados meteorológicos e geoespaciais apresentados pelos agentes especialistas."
    )

    return {
        "meteorologico": meteorologico,
        "geoespacial": geoespacial,
        "analise_alertas": analise_alertas,
        "coordenador": coordenador,
        "contribuicoes_ieap": contrib,
        "componente_dominante": dominante,
    }


def executar_fluxo_dashboard(cidade: str, usar_coordenador_llm: bool = False) -> dict:
    if cidade not in CIDADES:
        raise ValueError(f"Cidade não suportada: {cidade}")

    # Dashboard orientado à tarefa: os dados estruturados são obtidos uma vez e o IEAP
    # é sempre calculado pela função determinística consolidada no notebook v06.
    previsao = obter_previsao_openweather(cidade)
    historico = obter_historico_chuva_openmeteo(cidade)
    relevo = obter_relevo_openmeteo(cidade)

    indice = calcular_indice_atencao(
        chuva_24h_mm=previsao["chuva_24h_mm"],
        chuva_72h_mm=previsao["chuva_72h_mm"],
        maior_chuva_3h_mm=previsao["maior_chuva_3h_mm"],
        umidade_media_72h_pct=previsao["umidade_media_72h_pct"],
        p95_historico_diario_mm=historico["p95_diario_mm"],
    )

    analise_blocos = _gerar_analise_multiagente(cidade, previsao, historico, relevo, indice)

    return {
        "cidade": cidade,
        "uf": CIDADES[cidade]["uf"],
        "previsao": previsao,
        "historico": historico,
        "relevo": relevo,
        "indice": indice,
        "analise_blocos": analise_blocos,
        "agentes": [
            "Agente Meteorológico",
            "Agente Geoespacial",
            "Agente de Análise e Alertas",
            "Agente Coordenador",
        ],
        "atualizado_em": datetime.now(),
    }
