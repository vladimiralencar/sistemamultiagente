import html
import re
from datetime import datetime
import streamlit as st

from config import CIDADES
from services.dashboard_service import executar_fluxo_dashboard

st.set_page_config(
    page_title="Sistema Multiagente — Análise de Inundações Urbanas",
    layout="wide",
    initial_sidebar_state="expanded",
)


def risk_style(nivel: str):
    return {
        "Baixa": ("BAIXA", "#10B759"),
        "Moderada": ("MODERADA", "#FBBF24"),
        "Alta": ("ALTA", "#F97316"),
        "Muito alta": ("MUITO ALTA", "#EF233C"),
    }.get(nivel, (nivel.upper(), "#64748B"))


def formatar_frases(texto: str) -> str:
    """Exibe cada frase em uma linha, preservando o conteúdo da análise."""
    frases = re.split(r"(?<=[.!?])\s+", texto.strip())
    return "".join(
        f'<div class="analysis-sentence">{html.escape(frase.strip())}</div>'
        for frase in frases if frase.strip()
    )


def icon_svg(name: str, cls: str = "icon-svg") -> str:
    icons = {
        "analysis": '<svg class="{cls}" viewBox="0 0 24 24"><path d="M4 20V10"/><path d="M10 20V4"/><path d="M16 20v-7"/><path d="M22 20V7"/></svg>',
        "home": '<svg class="{cls}" viewBox="0 0 24 24"><path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 10.5V20h13v-9.5"/><path d="M9.5 20v-6h5v6"/></svg>',
        "info": '<svg class="{cls}" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 10v6"/><path d="M12 7h.01"/></svg>',
        "mail": '<svg class="{cls}" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m4 7 8 6 8-6"/></svg>',
        "rain": '<svg class="{cls}" viewBox="0 0 24 24"><path d="M7 16h10a4 4 0 0 0 .6-7.95A6 6 0 0 0 6.3 9.5 3.5 3.5 0 0 0 7 16Z"/><path d="m8 19-1 2"/><path d="m12 19-1 2"/><path d="m16 19-1 2"/></svg>',
        "rain_peak": '<svg class="{cls}" viewBox="0 0 24 24"><path d="M4 20V12"/><path d="M9 20V7"/><path d="M14 20V3"/><path d="M19 20v-10"/><path d="M2 20h20"/></svg>',
        "elevation": '<svg class="{cls}" viewBox="0 0 24 24"><path d="m3 20 7-14 4 8 2-4 5 10H3Z"/><path d="m10 6 1.6 3.2"/></svg>',
        "clock": '<svg class="{cls}" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
        "agents": '<svg class="{cls}" viewBox="0 0 24 24"><circle cx="12" cy="5" r="2"/><circle cx="5" cy="18" r="2"/><circle cx="19" cy="18" r="2"/><path d="M12 7v4"/><path d="m12 11-7 5"/><path d="m12 11 7 5"/></svg>',
        "pin": '<svg class="{cls}" viewBox="0 0 24 24"><path d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/></svg>',
    }
    return icons[name].format(cls=cls)


st.markdown("""
<style>
:root{--navy:#062F56;--text:#0A2F78;--gold:#F4B51E;--border:#D9E8F4}
html,body,[class*="css"]{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.stApp{background:linear-gradient(135deg,#fff 0%,#F6FBFF 100%)}
header[data-testid="stHeader"]{background:rgba(255,255,255,.96)}
.block-container{padding-top:4.9rem;padding-bottom:1.5rem;max-width:1500px}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#05335A 0%,#062E51 50%,#032B4B 100%);border-right:1px solid rgba(255,255,255,.08)}
section[data-testid="stSidebar"]>div{padding-top:1rem}.sidebar-brand{padding:.2rem .45rem 1rem}.brand-line{font-weight:900;font-size:2rem;color:white}.brand-line span{color:#F5B82E}.brand-rule{width:82px;height:4px;border-radius:4px;background:#F5B82E;margin-top:18px}
.sidebar-panel{background:linear-gradient(180deg,rgba(17,93,151,.65),rgba(9,70,121,.72));border:1px solid rgba(116,188,236,.25);border-radius:12px;padding:16px;margin-top:8px}.sidebar-title{color:white;font-weight:800;font-size:1.15rem;margin-bottom:.65rem}.sidebar-help{color:white;opacity:.93;font-size:.96rem;margin-bottom:.5rem}section[data-testid="stSidebar"] label{color:white!important;font-weight:600}
.side-nav{margin-top:2rem}.side-item{color:white;padding:.86rem 1rem;border-radius:9px;margin:.25rem 0;font-size:1.03rem;display:flex;align-items:center;gap:12px}.side-item.active{background:linear-gradient(90deg,rgba(16,100,165,.9),rgba(12,76,132,.65));font-weight:700}
.icon-svg{width:22px;height:22px;stroke:currentColor;fill:none;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round;flex:0 0 auto}

.title{color:#082E79;font-weight:900;font-size:clamp(2rem,2.7vw,2.85rem);line-height:1.12;letter-spacing:-1px;margin:0 0 .7rem;max-width:1180px;overflow:visible}.gold-rule{width:74px;height:4px;background:#F4B51E;border-radius:99px;margin:.7rem 0 1.45rem}.city-title{color:#082E79;font-weight:900;font-size:2rem;margin-bottom:.7rem}
.metric-card,.section-card{background:rgba(255,255,255,.94);border:1px solid var(--border);border-radius:14px;box-shadow:0 6px 20px rgba(8,47,120,.055)}
.metric-card{position:relative;overflow:hidden;padding:18px 18px 22px;min-height:172px;display:flex;flex-direction:column;justify-content:space-between;transition:transform .16s ease,box-shadow .16s ease}
.metric-card:hover{box-shadow:0 8px 22px rgba(8,47,120,.075)}
.metric-card::after{content:"";position:absolute;left:-8%;right:-8%;bottom:-42px;height:82px;border-radius:50% 55% 0 0/44% 48% 0 0;background:var(--metric-wave,#EDF6FF);opacity:.95;z-index:0}
.metric-top,.metric-bottom{position:relative;z-index:1}.metric-top{display:flex;align-items:center;gap:13px}.metric-icon{width:46px;height:46px;border-radius:50%;background:var(--metric-icon-bg,#EAF4FF);color:var(--metric-icon,#087CE5);display:flex;align-items:center;justify-content:center;flex:0 0 auto}.metric-icon .icon-svg{width:28px;height:28px;stroke-width:2}.metric-label{color:#143D72;font-size:.94rem;line-height:1.25;font-weight:600}.metric-value{color:#082E79;font-weight:900;font-size:2.25rem;line-height:1;margin-top:18px;letter-spacing:-.8px}.metric-unit{font-size:1.05rem;font-weight:800;color:#315887;margin-left:4px;letter-spacing:0}.metric-date{font-size:1.12rem;line-height:1.25;letter-spacing:0}.metric-time{font-size:1rem;color:#315887;margin-top:3px;font-weight:800}.metric-rain{--metric-icon-bg:#EAF4FF;--metric-icon:#087CE5;--metric-wave:#E9F4FF}.metric-peak{--metric-icon-bg:#F0EDFF;--metric-icon:#4A46D8;--metric-wave:#EEEAFE}.metric-elevation{--metric-icon-bg:#EAF8EE;--metric-icon:#169447;--metric-wave:#E6F6EA}.metric-update{--metric-icon-bg:#FFF6DE;--metric-icon:#B88700;--metric-wave:#FFF3D4}
.section-card{padding:18px 20px;overflow:hidden}.section-title{color:#082E79;font-size:1.35rem;font-weight:900;margin-bottom:14px}
.ieap-shell{background:linear-gradient(135deg,#F3FFF7 0%,#EEFBF2 100%);border:1px solid #DDEFE3;border-radius:12px;padding:20px}.ieap-top{display:grid;grid-template-columns:1fr 1px 1.4fr;align-items:center;gap:28px;min-height:132px}.ieap-score{font-size:4.8rem;line-height:.95;color:#079347;font-weight:900;letter-spacing:-3px;text-align:center}.ieap-divider{width:1px;height:108px;background:#B9CFBF}.ieap-status{color:white;border-radius:11px;padding:16px 18px;text-align:center;font-size:1.55rem;font-weight:900}.legend-wrap{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:18px}.legend-item{text-align:center;color:#0A2F78;font-size:.93rem}.legend-bar{height:22px;border-radius:999px;margin-bottom:10px}.legend-name{font-weight:800}
.data-table{width:100%;border-collapse:collapse;overflow:hidden;border:1px solid #D9E8F4;border-radius:10px}.data-table th{background:#F1F6FB;color:#082E79;text-align:left;font-weight:800;padding:9px 12px}.data-table td{color:#143D72;padding:9px 12px;border-top:1px solid #E4EDF4}.analysis-text{color:#153F75;font-size:.98rem;line-height:1.55}.analysis-sentence{display:block;margin-bottom:5px}.analysis-sentence:last-child{margin-bottom:0}.analysis-block{padding:0 0 13px;margin:0 0 13px;border-bottom:1px solid #E4EDF4}.analysis-block:last-child{border-bottom:0;margin-bottom:0;padding-bottom:0}.analysis-agent{color:#082E79;font-weight:850;font-size:1rem;margin-bottom:5px}.coordinator-block{background:#F5F9FD;border:1px solid #DDEAF4!important;border-radius:9px;padding:12px 14px!important;margin-top:4px!important}.agents{border-left:1px solid #B9CAD9;padding-left:28px}.agent-head{display:flex;align-items:center;gap:10px}.agent-row{display:flex;gap:12px;align-items:flex-start;margin:10px 0}.check{width:14px;height:14px;border-radius:50%;background:#0DB153;display:flex;align-items:center;justify-content:center;flex:0 0 auto;margin-top:5px}.agent-title{color:#082E79;font-weight:800}.agent-desc{color:#264F7B;font-size:.88rem}.page-card{background:rgba(255,255,255,.96);border:1px solid var(--border);border-radius:12px;box-shadow:0 2px 8px rgba(8,47,120,.03);padding:28px 30px;margin-top:10px;color:#153F75;line-height:1.65}.page-card h2{color:#082E79;margin-top:0}.page-card h3{color:#082E79;margin-top:22px;margin-bottom:7px}.page-card a{color:#0A66C2;text-decoration:none;font-weight:700}.page-card a:hover{text-decoration:underline}.footer{border-top:1px solid #D8E6F1;margin-top:18px;padding-top:12px;text-align:right;color:#234C7D;font-size:.84rem}.footer a{color:#082E79!important;text-decoration:none!important;font-weight:800}.footer a:hover{color:#082E79!important;text-decoration:none!important}.footer a:focus-visible,.page-card a:focus-visible,.sidebar-brand-bottom a:focus-visible{outline:3px solid #F4B51E;outline-offset:3px;border-radius:4px}

/* Layout aprovado: menu limpo, cidade centralizada no fluxo lateral e marca no rodapé */
section[data-testid="stSidebar"]>div{display:flex;flex-direction:column;min-height:100vh;padding-top:1.15rem}
.nav-caption{color:#D8EAF7;font-size:.74rem;font-weight:800;letter-spacing:.11em;text-transform:uppercase;padding:.15rem .35rem .45rem;opacity:.9}

.nav-list{display:flex;flex-direction:column;gap:.42rem;margin-top:.1rem}
.nav-link{position:relative;display:flex;align-items:center;gap:13px;min-height:52px;padding:.82rem .95rem;border-radius:10px;border:1px solid transparent;color:white!important;text-decoration:none!important;font-size:1rem;font-weight:650;transition:background .15s ease,border-color .15s ease,box-shadow .15s ease}
.nav-link:hover{background:rgba(255,255,255,.07);color:white!important;text-decoration:none!important}
.nav-link:focus-visible{outline:3px solid rgba(244,181,30,.95);outline-offset:2px}
.nav-link.active{background:linear-gradient(90deg,#1478C6,#0E5F9F);box-shadow:0 5px 16px rgba(0,0,0,.12);font-weight:850}
.nav-link .icon-svg{width:22px;height:22px;color:white}
.side-divider{height:1px;background:rgba(255,255,255,.22);margin:1.15rem .35rem 1.25rem}
.city-head{display:flex;align-items:center;gap:9px;color:white;font-weight:800;margin:0 .35rem .55rem;font-size:.98rem}.city-head .icon-svg{width:19px;height:19px}
.sidebar-spacer{flex:1;min-height:8rem}
.sidebar-brand-bottom{margin:.7rem .35rem 1rem;padding:1rem;border-radius:12px;background:rgba(1,28,51,.2);text-align:left;border:1px solid rgba(255,255,255,.04)}
.sidebar-brand-bottom .brand{font-weight:900;font-size:1.35rem;color:white}.sidebar-brand-bottom .brand span{color:#F5B82E}.sidebar-brand-bottom .tagline{color:#C9DCEB;font-size:.84rem;margin-top:.25rem}.sidebar-brand-bottom .mini-rule{height:1px;background:rgba(255,255,255,.22);margin:1rem 0}.sidebar-brand-bottom .copyright{color:#E7F1F8;font-size:.78rem;line-height:1.55}.sidebar-brand-bottom a{color:#E7F1F8!important;text-decoration:none!important}.sidebar-brand-bottom a:hover{color:white!important;text-decoration:none!important}
.title{font-weight:950;font-size:clamp(2.1rem,2.85vw,3rem);line-height:1.08;letter-spacing:-1.2px;max-width:1220px}.gold-rule{width:88px}

@media(max-width:900px){.block-container{padding-top:5rem}.ieap-top{grid-template-columns:1fr;gap:12px}.ieap-divider{display:none}.legend-wrap{grid-template-columns:repeat(2,1fr)}.agents{border-left:0;padding-left:0;margin-top:12px}.title{font-size:2rem}}
</style>
""", unsafe_allow_html=True)

# Navegação em HTML para evitar os marcadores nativos do st.radio no deploy.
page_key = st.query_params.get("page", "analise")
if isinstance(page_key, list):
    page_key = page_key[0] if page_key else "analise"
page_key = str(page_key).lower()
page_map = {"analise": "Análise", "sobre": "Sobre o projeto", "contato": "Contato"}
pagina = page_map.get(page_key, "Análise")

with st.sidebar:
    st.markdown('<div class="nav-caption">Navegação</div>', unsafe_allow_html=True)
    nav_html = '<div class="nav-list">'
    for key, label, icon in [
        ("analise", "Análise", "home"),
        ("sobre", "Sobre o projeto", "info"),
        ("contato", "Contato", "mail"),
    ]:
        active = " active" if pagina == label else ""
        nav_html += (
            f'<a class="nav-link{active}" href="?page={key}">'
            f'{icon_svg(icon)}<span>{label}</span></a>'
        )
    nav_html += '</div>'
    st.markdown(nav_html, unsafe_allow_html=True)
    st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="city-head">{icon_svg("pin")}<span>Cidade</span></div>', unsafe_allow_html=True)
    city = st.selectbox("Cidade", list(CIDADES.keys()), label_visibility="collapsed")
    st.markdown('<div class="sidebar-spacer"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-brand-bottom">
      <a href="https://www.lananexus.org" target="_blank" rel="noopener noreferrer" aria-label="Abrir site da LANA NEXUS"><div class="brand">LANA <span>NEXUS</span></div></a>
      <div class="tagline">Tecnologia para a vida</div>
      <div class="mini-rule"></div>
      <div class="copyright">© 2026 LANA NEXUS<br><a href="https://www.lananexus.org" target="_blank" rel="noopener noreferrer">www.lananexus.org</a></div>
    </div>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=3600, show_spinner=False)
def carregar_dashboard(cidade: str):
    return executar_fluxo_dashboard(cidade, usar_coordenador_llm=False)

if pagina == "Sobre o projeto":
    st.markdown('<div class="title">Sobre o projeto</div>', unsafe_allow_html=True)
    st.markdown('<div class="gold-rule"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="page-card">
      <h2>Sistema Multiagente para Análise de Inundações Urbanas</h2>
      <p>Este projeto apresenta um protótipo experimental de sistema multiagente para análise de condições ambientais associadas à atenção pluviométrica em áreas urbanas.</p>
      <p>A arquitetura distribui responsabilidades entre agentes especializados, permitindo coletar dados ambientais, analisar informações meteorológicas e geoespaciais e produzir uma síntese integrada.</p>
      <h3>Arquitetura multiagente</h3>
      <p><strong>Agente Meteorológico:</strong> consulta previsão e histórico de precipitação e organiza os indicadores meteorológicos utilizados pelo sistema.</p>
      <p><strong>Agente Geoespacial:</strong> obtém informações simplificadas de elevação para caracterização complementar do relevo.</p>
      <p><strong>Agente de Análise e Alertas:</strong> calcula e interpreta o Índice Experimental de Atenção Pluviométrica (IEAP).</p>
      <p><strong>Agente Coordenador:</strong> integra os resultados dos especialistas e produz a síntese final da análise.</p>
      <h3>Índice experimental</h3>
      <p>O IEAP utiliza precipitação prevista em 24 e 72 horas, maior chuva prevista em uma janela de 3 horas, umidade média e o P95 histórico diário de precipitação. O relevo é apresentado separadamente e não participa da fórmula do índice.</p>
      <h3>Limitações</h3>
      <p>O protótipo não constitui modelo hidrológico validado nem sistema oficial de alerta. Nesta versão, não incorpora drenagem urbana, impermeabilização do solo, níveis de rios e canais, marés, microtopografia ou ocorrências em tempo real. Seus resultados devem ser interpretados como apoio experimental à análise pluviométrica.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="footer">© 2026 LANA NEXUS — <a href="https://www.lananexus.org" target="_blank" rel="noopener noreferrer">www.lananexus.org</a></div>', unsafe_allow_html=True)
    st.stop()

if pagina == "Contato":
    st.markdown('<div class="title">Contato</div>', unsafe_allow_html=True)
    st.markdown('<div class="gold-rule"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="page-card">
      <h2>LANA NEXUS</h2>
      <p>Para informações sobre o projeto, pesquisa, desenvolvimento e possíveis colaborações, entre em contato com a LANA NEXUS.</p>
      <h3>Website</h3>
      <p><a href="https://www.lananexus.org" target="_blank" rel="noopener noreferrer">www.lananexus.org</a></p>
      <h3>Projeto</h3>
      <p>Sistema Multiagente para Análise de Inundações Urbanas.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="footer">© 2026 LANA NEXUS — <a href="https://www.lananexus.org" target="_blank" rel="noopener noreferrer">www.lananexus.org</a></div>', unsafe_allow_html=True)
    st.stop()

st.markdown('<div class="title">Sistema Multiagente para Análise de Inundações Urbanas</div>', unsafe_allow_html=True)
st.markdown('<div class="gold-rule"></div>', unsafe_allow_html=True)

try:
    with st.spinner("Consultando agentes e dados ambientais..."):
        result = carregar_dashboard(city)
except Exception as exc:
    st.error(f"Não foi possível atualizar a análise: {exc}")
    st.info("Confira o arquivo .env e a conexão com as APIs. O projeto não contém chaves secretas embutidas.")
    st.stop()

p = result["previsao"]
h = result["historico"]
r = result["relevo"]
i = result["indice"]
status, status_color = risk_style(i["nivel_atencao"])

st.markdown(f'<div class="city-title">{html.escape(city)} ({result["uf"]})</div>', unsafe_allow_html=True)

atualizado_data = result["atualizado_em"].strftime("%d/%m/%Y")
atualizado_hora = result["atualizado_em"].strftime("%H:%M")
m1, m2, m3, m4, m5 = st.columns(5, gap="medium")
metrics = [
    (m1, "metric-rain", icon_svg("rain"), "Chuva prevista<br>em 24 horas", f'{p["chuva_24h_mm"]:.2f}', "mm"),
    (m2, "metric-rain", icon_svg("rain"), "Chuva prevista<br>em 72 horas", f'{p["chuva_72h_mm"]:.2f}', "mm"),
    (m3, "metric-peak", icon_svg("rain_peak"), "Maior chuva<br>em 3 horas", f'{p["maior_chuva_3h_mm"]:.2f}', "mm"),
    (m4, "metric-elevation", icon_svg("elevation"), "Elevação<br>média", f'{r["elevacao_media_m"]:.1f}', "m"),
]
for col, css_class, icon, label, value, unit in metrics:
    with col:
        card_html = (
            f'<div class="metric-card {css_class}">'
            f'<div class="metric-top"><div class="metric-icon">{icon}</div><div class="metric-label">{label}</div></div>'
            f'<div class="metric-bottom"><div class="metric-value">{value}<span class="metric-unit">{unit}</span></div></div>'
            f'</div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)
with m5:
    update_html = (
        f'<div class="metric-card metric-update">'
        f'<div class="metric-top"><div class="metric-icon">{icon_svg("clock")}</div><div class="metric-label">Última<br>atualização</div></div>'
        f'<div class="metric-bottom"><div class="metric-value metric-date">{atualizado_data}</div><div class="metric-time">{atualizado_hora}</div></div>'
        f'</div>'
    )
    st.markdown(update_html, unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
left, right = st.columns([1.05, 1])
with left:
    st.markdown(f'''<div class="section-card"><div class="section-title">Índice Experimental de Atenção Pluviométrica</div><div class="ieap-shell"><div class="ieap-top"><div class="ieap-score">{i["score_0_100"]:.1f}</div><div class="ieap-divider"></div><div class="ieap-status" style="background:{status_color}">{status}</div></div><div class="legend-wrap"><div class="legend-item"><div class="legend-bar" style="background:#11B45C"></div><div class="legend-name">Baixa</div><div>0 – 24,9</div></div><div class="legend-item"><div class="legend-bar" style="background:#FBBF24"></div><div class="legend-name">Moderada</div><div>25 – 49,9</div></div><div class="legend-item"><div class="legend-bar" style="background:#F97316"></div><div class="legend-name">Alta</div><div>50 – 74,9</div></div><div class="legend-item"><div class="legend-bar" style="background:#EF233C"></div><div class="legend-name">Muito alta</div><div>75 – 100</div></div></div></div></div>''', unsafe_allow_html=True)
with right:
    rows = [
        ("Chuva prevista em 24h", f'{p["chuva_24h_mm"]:.2f} mm'),
        ("Chuva prevista em 72h", f'{p["chuva_72h_mm"]:.2f} mm'),
        ("Maior chuva em 3h", f'{p["maior_chuva_3h_mm"]:.2f} mm'),
        ("Umidade média em 72h", f'{p["umidade_media_72h_pct"]:.1f}%'),
        ("Vento máximo em 72h", f'{p["vento_max_72h_ms"]:.1f} m/s'),
        ("P95 histórico diário", f'{h["p95_diario_mm"]:.2f} mm'),
        ("Elevação média", f'{r["elevacao_media_m"]:.1f} m'),
    ]
    html_rows = ''.join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in rows)
    st.markdown(f'<div class="section-card"><div class="section-title">Dados ambientais utilizados</div><table class="data-table"><thead><tr><th>Indicador</th><th>Valor</th></tr></thead><tbody>{html_rows}</tbody></table></div>', unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-card">', unsafe_allow_html=True)
b1, b2 = st.columns([1.7, .85])
with b1:
    st.markdown('<div class="section-title">Análise do sistema multiagente</div>', unsafe_allow_html=True)
    blocos = result["analise_blocos"]
    analise_html = f"""
    <div class="analysis-block"><div class="analysis-agent">Agente Meteorológico</div>
    <div class="analysis-text">{formatar_frases(blocos['meteorologico'])}</div></div>
    <div class="analysis-block"><div class="analysis-agent">Agente Geoespacial</div>
    <div class="analysis-text">{formatar_frases(blocos['geoespacial'])}</div></div>
    <div class="analysis-block"><div class="analysis-agent">Agente de Análise e Alertas</div>
    <div class="analysis-text">{formatar_frases(blocos['analise_alertas'])}</div></div>
    <div class="analysis-block coordinator-block"><div class="analysis-agent">Síntese do Agente Coordenador</div>
    <div class="analysis-text">{formatar_frases(blocos['coordenador'])}</div></div>
    """
    st.markdown(analise_html, unsafe_allow_html=True)
with b2:
    st.markdown(f'''<div class="agents"><div class="agent-head"><span style="color:#0A74D8">{icon_svg("agents")}</span><div class="section-title" style="font-size:1.05rem;margin:0">Agentes envolvidos</div></div><div class="agent-row"><div class="check"></div><div><div class="agent-title">Agente Meteorológico</div><div class="agent-desc">Previsão e histórico de precipitação</div></div></div><div class="agent-row"><div class="check"></div><div><div class="agent-title">Agente Geoespacial</div><div class="agent-desc">Grade simplificada de elevação</div></div></div><div class="agent-row"><div class="check"></div><div><div class="agent-title">Agente de Análise e Alertas</div><div class="agent-desc">Cálculo do IEAP e interpretação</div></div></div><div class="agent-row"><div class="check"></div><div><div class="agent-title">Agente Coordenador</div><div class="agent-desc">Integração e síntese dos especialistas</div></div></div></div>''', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="footer">© 2026 LANA NEXUS — <a href="https://www.lananexus.org" target="_blank" rel="noopener noreferrer">www.lananexus.org</a></div>', unsafe_allow_html=True)
