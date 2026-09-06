# Sistema Multiagente para Análise de Inundações Urbanas

Sistema experimental multiagente para análise de atenção pluviométrica e apoio à análise de inundações urbanas, integrando dados meteorológicos, históricos e geoespaciais.

Desenvolvido no contexto das atividades de pesquisa da **LANA NEXUS**.

## Aplicação

O sistema está disponível publicamente no Streamlit:

**[Acessar o Sistema Multiagente](https://sistemamultiagente.streamlit.app/)**

---

## Sobre o projeto

O **Sistema Multiagente para Análise de Inundações Urbanas** é um protótipo experimental desenvolvido para integrar diferentes fontes de dados ambientais e organizar sua análise por meio de agentes especializados.

Nesta versão, o sistema trabalha com três áreas-piloto:

- Campina Grande (PB)
- João Pessoa (PB)
- Recife (PE)

Ao selecionar uma cidade, o sistema obtém e processa automaticamente informações meteorológicas, dados históricos de precipitação e informações simplificadas de elevação.

Os resultados são apresentados em um dashboard interativo, incluindo o **Índice Experimental de Atenção Pluviométrica (IEAP)** e a análise produzida pela arquitetura multiagente.

## Arquitetura multiagente

A arquitetura do sistema é organizada em quatro agentes com responsabilidades distintas.

### Agente Meteorológico

Responsável pela análise das condições meteorológicas e do histórico de precipitação.

Entre os dados utilizados estão:

- chuva prevista em 24 horas;
- chuva prevista em 72 horas;
- maior acumulado de chuva em uma janela de 3 horas;
- umidade média prevista;
- vento máximo previsto;
- precipitação histórica;
- percentil P95 da precipitação diária histórica.

### Agente Geoespacial

Responsável pela análise das informações geoespaciais disponíveis.

Nesta versão, utiliza uma grade simplificada de elevação para obter:

- elevação mínima;
- elevação média;
- elevação máxima;
- amplitude altimétrica.

Os dados de relevo são utilizados como informação complementar e **não participam da fórmula do IEAP**.

### Agente de Análise e Alertas

Responsável pela interpretação dos dados ambientais e pelo cálculo do **Índice Experimental de Atenção Pluviométrica (IEAP)**.

O agente utiliza os resultados meteorológicos e históricos para classificar o nível de atenção pluviométrica.

### Agente Coordenador

Responsável pela integração e síntese dos resultados produzidos pelos agentes especializados.

A arquitetura mantém separadas as informações meteorológicas e geoespaciais quando não existe um modelo validado que permita combiná-las quantitativamente.

## Índice Experimental de Atenção Pluviométrica — IEAP

O **IEAP** é um indicador experimental utilizado pelo sistema para representar o nível de atenção associado às condições pluviométricas analisadas.

O cálculo considera:

- precipitação prevista em 24 horas;
- precipitação prevista em 72 horas;
- maior precipitação prevista em uma janela de 3 horas;
- umidade média prevista em 72 horas;
- P95 histórico da precipitação diária.

O índice varia de **0 a 100**.

| IEAP | Classificação |
|---|---|
| 0 – 24,9 | Baixa |
| 25 – 49,9 | Moderada |
| 50 – 74,9 | Alta |
| 75 – 100 | Muito alta |

O relevo é apresentado separadamente e não integra o cálculo do índice.

> **Observação metodológica:** o IEAP é um indicador experimental de atenção pluviométrica. Não constitui um modelo hidrológico validado nem um sistema oficial de alerta de inundações.

## Fontes de dados

### OpenWeatherMap

Utilizado para previsão meteorológica em intervalos de 3 horas.

A partir dessas previsões são calculados indicadores como chuva acumulada em 24 e 72 horas, maior precipitação em 3 horas, umidade média e vento máximo.

### Open-Meteo Historical Weather

Utilizado para obtenção do histórico diário de precipitação.

Os dados históricos permitem calcular estatísticas de referência, incluindo o **P95 da precipitação diária** utilizado pelo IEAP.

### Open-Meteo Elevation

Utilizado para obtenção dos dados simplificados de elevação.

A fonte de elevação utilizada pelo serviço está associada ao **Copernicus DEM GLO-90**.

## Fluxo de funcionamento

A seleção da cidade atualiza automaticamente o dashboard.

```text
Seleção da cidade
        │
        ▼
Coleta de dados ambientais
        │
        ├── Previsão meteorológica
        ├── Histórico de precipitação
        └── Dados de elevação
        │
        ▼
Processamento dos dados
        │
        ├── Agente Meteorológico
        └── Agente Geoespacial
        │
        ▼
Cálculo determinístico do IEAP
        │
        ▼
Agente de Análise e Alertas
        │
        ▼
Agente Coordenador
        │
        ▼
Dashboard e síntese da análise
```

O cálculo do IEAP permanece determinístico, garantindo que a interpretação textual não altere o valor calculado pelo modelo.

## Dashboard

O dashboard apresenta:

- indicadores meteorológicos principais;
- data e hora da última atualização;
- Índice Experimental de Atenção Pluviométrica;
- classificação do IEAP;
- dados ambientais utilizados;
- análise dos agentes;
- síntese do Agente Coordenador.

A mudança de cidade inicia automaticamente uma nova análise.

## Tecnologias

- Python
- Streamlit
- OpenWeatherMap API
- Open-Meteo API
- arquitetura baseada em agentes
- processamento de dados meteorológicos e geoespaciais

## Estrutura do projeto

```text
sistemamultiagente/
│
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── agents/
│   ├── motor.py
│   ├── meteorologico.py
│   ├── geoespacial.py
│   ├── analise_alertas.py
│   └── coordenador.py
│
├── core/
│   └── ieap.py
│
├── tools/
│   ├── meteorologia.py
│   └── geoespacial.py
│
├── services/
│   └── dashboard_service.py
│
└── tests/
    └── test_ieap.py
```

## Instalação

Clone o repositório:

```bash
git clone https://github.com/vladimiralencar/sistemamultiagente.git
cd sistemamultiagente
```

Crie um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute:

```bash
streamlit run app.py
```

## Variáveis de ambiente

As chaves de API **não devem ser armazenadas no repositório**.

Crie localmente o arquivo `.env` a partir do exemplo:

```bash
cp .env.example .env
```

Configure as variáveis necessárias no `.env`.

```text
OPENAI_API_KEY=sua_chave
OPENWEATHER_API_KEY=sua_chave
```

O arquivo `.env` deve permanecer listado no `.gitignore`.

Para implantação no **Streamlit Community Cloud**, as chaves devem ser configuradas utilizando o gerenciamento de secrets da plataforma, e não adicionadas ao GitHub.

## Origem e metodologia do projeto

A versão modular do sistema foi desenvolvida a partir do notebook consolidado do projeto de pesquisa:

`Projeto-04-AgenteIA-InundacaoUrbana-MariaHelena-Multiagente-v06.ipynb`

Foram preservados os principais elementos metodológicos do protótipo, incluindo:

- áreas-piloto;
- aquisição de previsão meteorológica;
- histórico de precipitação;
- informações de elevação;
- cálculo determinístico do IEAP;
- especialização dos agentes;
- separação metodológica entre atenção pluviométrica e relevo.

A aplicação Streamlit reorganiza esses componentes em uma arquitetura modular adequada à execução como aplicação web.

## Segurança

Nenhuma chave de API deve ser publicada no repositório.

Arquivos contendo credenciais locais, especialmente `.env`, devem permanecer fora do controle de versão.

Caso uma chave seja publicada acidentalmente, ela deve ser revogada e substituída imediatamente.

## Projeto de pesquisa

Este software é um **protótipo experimental de pesquisa**.

Os resultados produzidos devem ser interpretados dentro das limitações metodológicas do modelo e das fontes de dados utilizadas.

## LANA NEXUS

**Tecnologia para a vida**

[www.lananexus.org](https://www.lananexus.org)

© 2026 LANA NEXUS
