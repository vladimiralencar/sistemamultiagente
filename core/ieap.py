def calcular_indice_atencao(
    chuva_24h_mm: float,
    chuva_72h_mm: float,
    maior_chuva_3h_mm: float,
    umidade_media_72h_pct: float,
    p95_historico_diario_mm: float,
) -> dict:
    """Implementação fiel à função consolidada no notebook v06."""
    p95 = max(float(p95_historico_diario_mm), 1.0)

    chuva_24h_mm = float(chuva_24h_mm)
    chuva_72h_mm = float(chuva_72h_mm)
    maior_chuva_3h_mm = float(maior_chuva_3h_mm)
    umidade_media_72h_pct = float(umidade_media_72h_pct)

    r24 = chuva_24h_mm / p95
    r72 = chuva_72h_mm / (2.0 * p95)

    c24 = min(r24, 1.5) / 1.5 * 45
    c72 = min(r72, 1.5) / 1.5 * 30
    c3h = min(maior_chuva_3h_mm / 30.0, 1.0) * 20
    chum = max(0, min((umidade_media_72h_pct - 70) / 25, 1)) * 5

    score = round(float(c24 + c72 + c3h + chum), 1)

    if score < 25:
        nivel = "Baixa"
    elif score < 50:
        nivel = "Moderada"
    elif score < 75:
        nivel = "Alta"
    else:
        nivel = "Muito alta"

    return {
        "score_0_100": score,
        "nivel_atencao": nivel,
        "chuva_24h_mm": chuva_24h_mm,
        "chuva_72h_mm": chuva_72h_mm,
        "maior_chuva_3h_mm": maior_chuva_3h_mm,
        "umidade_media_72h_pct": umidade_media_72h_pct,
        "p95_historico_diario_mm": p95,
        "razao_24h_p95": round(float(r24), 2),
        "razao_72h_2p95": round(float(r72), 2),
        "observacao": (
            "Índice experimental de atenção pluviométrica. "
            "Não é modelo hidrológico validado nem alerta oficial."
        ),
    }
