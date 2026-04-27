import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "pipeline"))

from world_bank import fetch_world_bank, WB_INDICATORS
from hdi import fetch_hdi
from ilo import fetch_informality

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BAEZTRIVE Explore",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global styles ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Gabarito:wght@400;700;900&display=swap');

* { font-family: 'Gabarito', sans-serif !important; }

/* Background */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="block-container"] {
    background-color: #0C0C0C !important;
    color: #F4F4F4 !important;
}
[data-testid="stHeader"]  { background-color: #0C0C0C !important; }
[data-testid="stSidebar"] { background-color: #111111 !important; border-right: 1px solid #222; }

/* Sidebar labels */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stRadio label {
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #888 !important;
}

/* Selectbox & Radio */
div[data-testid="stSelectbox"] > div,
div[data-testid="stRadio"]     > div {
    background-color: #1A1A1A !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 2px !important;
}
div[data-testid="stSelectbox"]:focus-within,
div[data-testid="stRadio"]:focus-within {
    border-color: #F92B2B !important;
}

/* Metric cards */
.metric-card {
    background: #111111;
    border: 1px solid #1E1E1E;
    border-top: 3px solid #F92B2B;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.5rem;
}
.metric-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #555;
    margin-bottom: 0.3rem;
}
.metric-value {
    font-size: 2rem;
    font-weight: 900;
    color: #F4F4F4;
    line-height: 1;
}
.metric-delta-pos { font-size: 0.8rem; font-weight: 700; color: #22C55E; margin-top: 0.3rem; }
.metric-delta-neg { font-size: 0.8rem; font-weight: 700; color: #F92B2B; margin-top: 0.3rem; }
.metric-delta-neu { font-size: 0.8rem; font-weight: 700; color: #555;    margin-top: 0.3rem; }

/* Divider */
.red-divider { border: none; border-top: 1px solid #F92B2B; margin: 0.5rem 0 1.5rem 0; }

/* Data table */
.stDataFrame { border: 1px solid #1E1E1E !important; }

/* Spinner */
[data-testid="stSpinner"] p { color: #555 !important; font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase; }

/* Hide streamlit branding */
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
COUNTRIES = {
    "México":    {"wb": "MX",  "iso3": "MEX", "flag": "🇲🇽"},
    "Brasil":    {"wb": "BR",  "iso3": "BRA", "flag": "🇧🇷"},
    "Argentina": {"wb": "AR",  "iso3": "ARG", "flag": "🇦🇷"},
    "Colombia":  {"wb": "CO",  "iso3": "COL", "flag": "🇨🇴"},
    "Chile":     {"wb": "CL",  "iso3": "CHL", "flag": "🇨🇱"},
    "Perú":      {"wb": "PE",  "iso3": "PER", "flag": "🇵🇪"},
}

INDICATORS = [
    "PIB (USD)",
    "PIB per cápita (USD)",
    "Población",
    "Gini",
    "Pobreza extrema (%)",
    "IDH",
    "Informalidad laboral (%)",
]

INDICATOR_DESCRIPTIONS = {
    "PIB (USD)":              "Producto Interno Bruto a precios corrientes · Banco Mundial",
    "PIB per cápita (USD)":   "PIB dividido entre la población total · Banco Mundial",
    "Población":              "Población total estimada · Banco Mundial",
    "Gini":                   "Coeficiente de Gini (0 = igualdad total, 100 = desigualdad total) · Banco Mundial",
    "Pobreza extrema (%)":    "Población que vive con menos de $2.15 USD/día · Banco Mundial",
    "IDH":                    "Índice de Desarrollo Humano (0–1) · PNUD",
    "Informalidad laboral (%)": "Proporción de empleo informal SDG 8.3.1 · OIT",
}

COLORS = ["#F92B2B", "#FFFFFF", "#F97316", "#A78BFA", "#34D399", "#60A5FA"]

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem 0 1.5rem 0;">
        <div style="font-size:0.6rem;letter-spacing:4px;text-transform:uppercase;color:#F92B2B;font-weight:900;">
            BAEZTRIVE
        </div>
        <div style="font-size:1.4rem;font-weight:900;color:#F4F4F4;text-transform:uppercase;letter-spacing:-0.5px;">
            Explore
        </div>
        <div style="font-size:0.6rem;letter-spacing:2px;color:#444;text-transform:uppercase;margin-top:0.2rem;">
            Data Studios · LATAM
        </div>
    </div>
    <hr class="red-divider">
    """, unsafe_allow_html=True)

    modo = st.radio("Modo de análisis", ["País individual", "Vs Mode"], label_visibility="collapsed")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    if modo == "País individual":
        pais_sel = st.selectbox("País", list(COUNTRIES.keys()))
        paises_seleccionados = [pais_sel]
    else:
        pais1 = st.selectbox("País 1", list(COUNTRIES.keys()), index=0)
        pais2 = st.selectbox("País 2", list(COUNTRIES.keys()), index=1)
        paises_seleccionados = [pais1, pais2]

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    indicador = st.selectbox("Indicador", INDICATORS)

    st.markdown(f"""
    <div style="margin-top:1.5rem;padding:0.8rem;background:#0C0C0C;border-left:2px solid #F92B2B;">
        <div style="font-size:0.6rem;letter-spacing:2px;text-transform:uppercase;color:#555;margin-bottom:0.3rem;">Fuente</div>
        <div style="font-size:0.7rem;color:#888;line-height:1.5;">{INDICATOR_DESCRIPTIONS[indicador]}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Data fetching ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def get_data(pais, indicador):
    codes = COUNTRIES[pais]
    if indicador == "IDH":
        return fetch_hdi(codes["iso3"])
    elif indicador == "Informalidad laboral (%)":
        return fetch_informality(codes["iso3"])
    else:
        return fetch_world_bank(WB_INDICATORS[indicador], codes["wb"])

with st.spinner("Cargando datos..."):
    dfs = {}
    for pais in paises_seleccionados:
        df = get_data(pais, indicador)
        if not df.empty:
            dfs[pais] = df.set_index("year")["value"]

# ── Header ────────────────────────────────────────────────────────────────────
flag_str = " ".join(COUNTRIES[p]["flag"] for p in paises_seleccionados)
title_countries = " vs ".join(paises_seleccionados) if len(paises_seleccionados) > 1 else paises_seleccionados[0]

st.markdown(f"""
<div style="padding: 2rem 0 0.5rem 0;">
    <div style="font-size:0.65rem;letter-spacing:4px;text-transform:uppercase;color:#F92B2B;font-weight:900;margin-bottom:0.5rem;">
        {flag_str} &nbsp; {title_countries.upper()}
    </div>
    <div style="font-size:2.8rem;font-weight:900;color:#F4F4F4;text-transform:uppercase;letter-spacing:-1px;line-height:1;">
        {indicador}
    </div>
</div>
<hr class="red-divider">
""", unsafe_allow_html=True)

# ── Main content ──────────────────────────────────────────────────────────────
if not dfs:
    st.markdown("""
    <div style="padding:3rem;text-align:center;border:1px solid #1E1E1E;">
        <div style="font-size:0.75rem;letter-spacing:3px;text-transform:uppercase;color:#555;">
            No se encontraron datos para esta selección
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

combined = pd.DataFrame(dfs)

# ── Metric cards ──────────────────────────────────────────────────────────────
def format_value(val, ind):
    if ind == "PIB (USD)":
        if val >= 1e12: return f"${val/1e12:.2f}T"
        if val >= 1e9:  return f"${val/1e9:.1f}B"
        return f"${val:,.0f}"
    elif ind == "PIB per cápita (USD)":
        return f"${val:,.0f}"
    elif ind == "Población":
        if val >= 1e6: return f"{val/1e6:.1f}M"
        return f"{val:,.0f}"
    elif ind in ("Gini", "Pobreza extrema (%)", "Informalidad laboral (%)"):
        return f"{val:.1f}%"
    elif ind == "IDH":
        return f"{val:.3f}"
    return f"{val:,.2f}"

metric_cols = st.columns(len(dfs))
for i, (pais, serie) in enumerate(dfs.items()):
    latest_year = serie.dropna().index.max()
    latest_val  = serie.loc[latest_year]
    prev_years  = serie.dropna().index[serie.dropna().index < latest_year]
    flag        = COUNTRIES[pais]["flag"]

    if len(prev_years) > 0:
        prev_val   = serie.loc[prev_years.max()]
        delta_pct  = ((latest_val - prev_val) / prev_val) * 100
        arrow      = "▲" if delta_pct >= 0 else "▼"
        delta_cls  = "metric-delta-pos" if delta_pct >= 0 else "metric-delta-neg"
        delta_html = f'<div class="{delta_cls}">{arrow} {abs(delta_pct):.1f}% vs {prev_years.max()}</div>'
    else:
        delta_html = '<div class="metric-delta-neu">— sin dato anterior</div>'

    with metric_cols[i]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{flag} {pais} · {latest_year}</div>
            <div class="metric-value">{format_value(latest_val, indicador)}</div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ── Plotly chart ──────────────────────────────────────────────────────────────
fig = go.Figure()

for i, (pais, serie) in enumerate(dfs.items()):
    serie_clean = serie.dropna().sort_index()
    color = COLORS[i % len(COLORS)]
    flag  = COUNTRIES[pais]["flag"]

    fig.add_trace(go.Scatter(
        x=serie_clean.index,
        y=serie_clean.values,
        mode="lines+markers",
        name=f"{flag} {pais}",
        line=dict(color=color, width=2.5),
        marker=dict(size=5, color=color, symbol="circle"),
        hovertemplate=(
            f"<b>{flag} {pais}</b><br>"
            "Año: %{x}<br>"
            "Valor: %{y:,.3~g}<extra></extra>"
        ),
    ))

fig.update_layout(
    paper_bgcolor="#0C0C0C",
    plot_bgcolor="#0C0C0C",
    font=dict(family="Gabarito, sans-serif", color="#F4F4F4"),
    margin=dict(l=0, r=0, t=10, b=0),
    legend=dict(
        orientation="h",
        yanchor="bottom", y=1.02,
        xanchor="left",   x=0,
        bgcolor="rgba(0,0,0,0)",
        font=dict(size=13, color="#F4F4F4"),
    ),
    xaxis=dict(
        showgrid=True,
        gridcolor="#1A1A1A",
        gridwidth=1,
        zeroline=False,
        tickfont=dict(size=11, color="#555"),
        tickformat="d",
        linecolor="#222",
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="#1A1A1A",
        gridwidth=1,
        zeroline=False,
        tickfont=dict(size=11, color="#555"),
        linecolor="#222",
    ),
    hovermode="x unified",
    hoverlabel=dict(
        bgcolor="#1A1A1A",
        bordercolor="#F92B2B",
        font=dict(color="#F4F4F4", size=12),
    ),
    height=420,
)

st.plotly_chart(fig, use_container_width=True)

# ── Data table ────────────────────────────────────────────────────────────────
st.markdown("<hr class='red-divider'>", unsafe_allow_html=True)
st.markdown("""
<div style="font-size:0.65rem;letter-spacing:3px;text-transform:uppercase;color:#555;margin-bottom:0.8rem;font-weight:700;">
    Datos históricos
</div>
""", unsafe_allow_html=True)

display = combined.sort_index(ascending=False).copy()
display.index.name = "Año"
st.dataframe(
    display.style.format(lambda v: format_value(v, indicador) if pd.notna(v) else "—"),
    use_container_width=True,
    height=280,
)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:3rem;padding-top:1rem;border-top:1px solid #1A1A1A;
            display:flex;justify-content:space-between;align-items:center;">
    <div style="font-size:0.6rem;letter-spacing:3px;text-transform:uppercase;color:#333;font-weight:700;">
        BAEZTRIVE Data Studios
    </div>
    <div style="font-size:0.6rem;letter-spacing:2px;text-transform:uppercase;color:#333;">
        Fuentes: Banco Mundial · PNUD · OIT
    </div>
</div>
""", unsafe_allow_html=True)
