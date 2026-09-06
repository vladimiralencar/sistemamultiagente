from core.ieap import calcular_indice_atencao


def test_ieap_faixas():
    baixo = calcular_indice_atencao(0, 0, 0, 70, 10)
    assert baixo["score_0_100"] == 0.0
    assert baixo["nivel_atencao"] == "Baixa"


def test_ieap_limite_maximo():
    alto = calcular_indice_atencao(1000, 1000, 1000, 100, 1)
    assert alto["score_0_100"] == 100.0
    assert alto["nivel_atencao"] == "Muito alta"


def test_formula_notebook_v06():
    r = calcular_indice_atencao(15, 30, 10, 80, 20)
    # c24=22.5, c72=15, c3h=6.666..., chum=2 => 46.2
    assert r["score_0_100"] == 46.2
    assert r["nivel_atencao"] == "Moderada"
