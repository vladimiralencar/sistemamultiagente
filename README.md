# LANA NEXUS — Sistema Multiagente para Análise de Inundações Urbanas

Versão modular do dashboard Streamlit, refatorada a partir do notebook consolidado:
`Projeto-04-AgenteIA-InundacaoUrbana-MariaHelena-Multiagente-v06.ipynb`.

## O que foi preservado do notebook v06

- Áreas-piloto: Campina Grande/PB, João Pessoa/PB e Recife/PE.
- OpenWeatherMap para previsão de 5 dias / intervalos de 3h.
- Open-Meteo Historical Weather para histórico de precipitação.
- Open-Meteo Elevation / Copernicus DEM GLO-90 para elevação.
- Fórmula original de `calcular_indice_atencao()` sem alteração.
- Agente Meteorológico, Agente Geoespacial, Agente de Análise e Alertas e Agente Coordenador.
- Roteamento dinâmico do Coordenador via tool calling.
- Separação metodológica entre atenção pluviométrica (IEAP) e relevo.

## Segurança

Nenhuma chave do notebook foi copiada para este projeto. Crie um `.env` local a partir de `.env.example`.

```bash
cp .env.example .env
```

Preencha:

```text
OPENAI_API_KEY=sua_chave
OPENWEATHER_API_KEY=sua_chave
```

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Estrutura

```text
projetomultiagentev01/
├── app.py
├── config.py
├── .env.example
├── requirements.txt
├── agents/
│   ├── motor.py
│   ├── meteorologico.py
│   ├── geoespacial.py
│   ├── analise_alertas.py
│   └── coordenador.py
├── core/
│   └── ieap.py
├── tools/
│   ├── meteorologia.py
│   └── geoespacial.py
├── services/
│   └── dashboard_service.py
└── tests/
    └── test_ieap.py
```

## Funcionamento do dashboard

A seleção da cidade atualiza automaticamente o painel. Não há botão “Executar análise”.

1. As ferramentas ambientais obtêm os dados estruturados reais.
2. O IEAP é calculado pela mesma função consolidada no notebook v06.
3. A seção “Análise do sistema multiagente” apresenta quatro blocos explicáveis: Agente Meteorológico, Agente Geoespacial, Agente de Análise e Alertas e Síntese do Agente Coordenador.
4. O texto do dashboard é gerado de forma determinística a partir dos mesmos dados estruturados e da mesma fórmula do notebook v06, evitando chamadas LLM redundantes e mantendo o resultado rápido e reproduzível.
5. A análise destaca o componente que mais contribuiu para o IEAP, sem alterar a fórmula consolidada.

## Observação metodológica

O IEAP é experimental, representa atenção pluviométrica e não incorpora relevo em sua fórmula. Não constitui modelo hidrológico validado nem alerta oficial.
