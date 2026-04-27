import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "pipeline"))

from world_bank import fetch_world_bank, WB_INDICATORS
from hdi import fetch_hdi
from ilo import fetch_informality

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BAEZTRIVE Explore",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# TOKENS
# ─────────────────────────────────────────────────────────────────────────────
RED    = "#F92B2B"
BLACK  = "#0A0A0A"
WHITE  = "#FFFFFF"
PAPER  = "#F4F3EF"   # warm off-white
BORDER = "#E2E1DB"
GRAY   = "#999893"
LGRAY  = "#CCCBC5"

PALETTE_LIGHT = ["#0A0A0A", "#F92B2B", "#2563EB", "#16A34A", "#D97706", "#7C3AED"]

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Gabarito:wght@400;700;900&family=IBM+Plex+Mono:wght@400;700&display=swap');

/* ── RESET ── */
*, *::before, *::after {{ box-sizing: border-box; }}
* {{ font-family: 'Gabarito', sans-serif !important; }}
.mono {{ font-family: 'IBM Plex Mono', monospace !important; }}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="block-container"],
[data-testid="stMainBlockContainer"] {{
    background-color: {PAPER} !important;
    color: {BLACK} !important;
}}
[data-testid="stHeader"] {{
    background-color: {PAPER} !important;
    border-bottom: 1px solid {BORDER};
}}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {{
    background-color: {WHITE} !important;
    border-right: 1px solid {BORDER} !important;
}}
[data-testid="stSidebar"] > div {{
    border-left: 4px solid {RED};
    padding-left: 1rem !important;
}}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {{
    font-size: 0.6rem !important;
    font-weight: 700 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    color: {GRAY} !important;
}}
[data-testid="stToggle"] label {{ font-size: 0.6rem !important; letter-spacing: 3px !important; }}
[data-testid="stSelectbox"] > div > div {{
    background: {PAPER} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 0 !important;
    font-weight: 700 !important;
}}

/* ── TABS ── */
[data-testid="stTabs"] [role="tablist"] {{
    background: {WHITE} !important;
    border-bottom: 2px solid {BORDER} !important;
    gap: 0 !important;
    padding: 0 !important;
}}
[data-testid="stTabs"] button[role="tab"] {{
    background: transparent !important;
    color: {LGRAY} !important;
    border: none !important;
    border-bottom: 4px solid transparent !important;
    border-radius: 0 !important;
    font-size: 0.6rem !important;
    font-weight: 900 !important;
    letter-spacing: 4px !important;
    text-transform: uppercase !important;
    padding: 1rem 2.5rem !important;
    margin-bottom: -2px !important;
}}
[data-testid="stTabs"] button[role="tab"]:hover {{
    color: {BLACK} !important;
    background: {PAPER} !important;
}}
[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {RED} !important;
    border-bottom: 4px solid {RED} !important;
    background: {PAPER} !important;
}}
[data-testid="stTabPanel"] {{
    background: {PAPER} !important;
    padding: 0 !important;
}}

/* ── SCROLLBAR ── */
::-webkit-scrollbar {{ width: 3px; height: 3px; }}
::-webkit-scrollbar-track {{ background: {PAPER}; }}
::-webkit-scrollbar-thumb {{ background: {LGRAY}; }}
::-webkit-scrollbar-thumb:hover {{ background: {RED}; }}

/* ── HIDE CHROME ── */
#MainMenu, footer, [data-testid="stDecoration"] {{ display: none !important; }}

/* ── HERO PANEL (RED BLOCK) ── */
.hero-block {{
    background: {RED};
    padding: 3rem 2.5rem 2.5rem;
    position: relative;
    overflow: hidden;
    min-height: 280px;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
}}
.hero-watermark {{
    position: absolute;
    top: -0.5rem;
    right: -1rem;
    font-size: 11rem;
    font-weight: 900;
    color: rgba(255,255,255,0.06);
    letter-spacing: -8px;
    line-height: 1;
    text-transform: uppercase;
    pointer-events: none;
    font-family: 'IBM Plex Mono', monospace !important;
    white-space: nowrap;
}}
.hero-kicker {{
    font-size: 0.58rem;
    font-weight: 900;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.5);
    margin-bottom: 0.8rem;
}}
.hero-number {{
    font-size: clamp(3rem, 6vw, 5.5rem);
    font-weight: 900;
    color: {WHITE};
    line-height: 0.9;
    letter-spacing: -2px;
    font-family: 'IBM Plex Mono', monospace !important;
    margin-bottom: 0.6rem;
}}
.hero-label {{
    font-size: 0.65rem;
    font-weight: 900;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.6);
}}
.hero-delta-up   {{ font-size: 0.75rem; font-weight: 700; color: rgba(255,255,255,0.85); margin-top: 0.5rem; }}
.hero-delta-down {{ font-size: 0.75rem; font-weight: 700; color: rgba(255,255,255,0.6);  margin-top: 0.5rem; }}
.hero-delta-flat {{ font-size: 0.75rem; font-weight: 700; color: rgba(255,255,255,0.4);  margin-top: 0.5rem; }}

/* ── STAT CARD (WHITE) ── */
.stat-card {{
    background: {WHITE};
    border: 1px solid {BORDER};
    border-top: 3px solid {BLACK};
    padding: 1.2rem 1.4rem;
}}
.stat-card.red-top {{ border-top-color: {RED}; }}
.stat-label {{
    font-size: 0.55rem;
    font-weight: 900;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: {GRAY};
    margin-bottom: 0.5rem;
}}
.stat-value {{
    font-size: 1.8rem;
    font-weight: 900;
    color: {BLACK};
    line-height: 1;
    letter-spacing: -0.5px;
    font-family: 'IBM Plex Mono', monospace !important;
}}
.stat-delta-up   {{ font-size: 0.7rem; font-weight: 700; color: #16A34A; margin-top: 0.3rem; }}
.stat-delta-down {{ font-size: 0.7rem; font-weight: 700; color: {RED};   margin-top: 0.3rem; }}
.stat-delta-flat {{ font-size: 0.7rem; font-weight: 700; color: {LGRAY}; margin-top: 0.3rem; }}

/* ── RANK ROW ── */
.rank-row {{
    display: flex;
    align-items: center;
    padding: 1.1rem 0;
    border-bottom: 1px solid {BORDER};
    gap: 1.2rem;
}}
.rank-row:last-child {{ border-bottom: none; }}
.rank-num {{
    font-size: 0.65rem;
    font-weight: 900;
    color: {LGRAY};
    width: 1.5rem;
    letter-spacing: 1px;
    font-family: 'IBM Plex Mono', monospace !important;
}}
.rank-country {{
    font-size: 1rem;
    font-weight: 900;
    color: {BLACK};
    text-transform: uppercase;
    letter-spacing: 1px;
    width: 8rem;
    flex-shrink: 0;
}}
.rank-bar-track {{
    flex: 1;
    height: 6px;
    background: {BORDER};
    position: relative;
    overflow: visible;
}}
.rank-bar-fill {{
    height: 100%;
    background: {BLACK};
    transition: width 0.3s;
    position: relative;
}}
.rank-bar-fill.leader {{ background: {RED}; }}
.rank-value {{
    font-size: 0.85rem;
    font-weight: 700;
    color: {BLACK};
    width: 6rem;
    text-align: right;
    font-family: 'IBM Plex Mono', monospace !important;
    flex-shrink: 0;
}}
.rank-value.leader {{ color: {RED}; }}

/* ── DIVIDER ── */
.div-line {{ border: none; border-top: 1px solid {BORDER}; margin: 2rem 0; }}
.div-line-heavy {{ border: none; border-top: 2px solid {BLACK}; margin: 1rem 0 2rem; }}

/* ── SECTION LABEL ── */
.sec-label {{
    font-size: 0.55rem;
    font-weight: 900;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: {LGRAY};
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}}
.sec-label::after {{
    content: '';
    flex: 1;
    height: 1px;
    background: {BORDER};
}}

/* ── SOURCE TAG ── */
.src-tag {{
    display: inline-block;
    font-size: 0.55rem;
    font-weight: 900;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: {RED};
    border: 1px solid {RED};
    padding: 0.2rem 0.5rem;
    margin-top: 0.3rem;
}}

/* ── FOOTER ── */
.pg-footer {{
    padding: 2rem 0 1rem;
    border-top: 2px solid {BLACK};
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-top: 4rem;
}}
.pg-footer-brand {{
    font-size: 0.6rem;
    font-weight: 900;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: {BLACK};
}}
.pg-footer-brand span {{ color: {RED}; }}
.pg-footer-src {{
    font-size: 0.55rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: {LGRAY};
    text-align: right;
}}

/* ── EXPLORAR STAT CARDS ── */
.xp-card {{
    background: {WHITE};
    border: 1px solid {BORDER};
    border-top: 2px solid {BLACK};
    padding: 1rem 1.2rem 1rem;
    height: 100%;
}}
.xp-card.accent {{ border-top-color: {RED}; }}
.xp-label {{
    font-size: 0.52rem;
    font-weight: 900;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: {LGRAY};
    margin-bottom: 0.5rem;
}}
.xp-value {{
    font-size: 1.6rem;
    font-weight: 900;
    color: {BLACK};
    letter-spacing: -0.5px;
    line-height: 1;
    font-family: 'IBM Plex Mono', monospace !important;
}}
.xp-sub {{
    font-size: 0.6rem;
    color: {LGRAY};
    margin-top: 0.2rem;
    letter-spacing: 1px;
}}
.xp-delta-up   {{ color: #16A34A; font-weight: 700; }}
.xp-delta-down {{ color: {RED};   font-weight: 700; }}
.xp-delta-flat {{ color: {LGRAY}; font-weight: 700; }}

/* ── COUNTRY STRIP LABEL ── */
.country-strip {{
    font-size: 0.55rem;
    font-weight: 900;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: {GRAY};
    padding: 1rem 0 0.6rem;
    border-top: 1px solid {BORDER};
    margin-top: 0.8rem;
}}
.country-strip:first-of-type {{ border-top: none; margin-top: 0; padding-top: 0; }}

/* ── MINI CHART CARD ── */
.mini-card {{
    background: {WHITE};
    border: 1px solid {BORDER};
    padding: 1rem 1rem 0;
    margin-bottom: 1rem;
}}
.mini-card-top {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.3rem;
}}
.mini-val {{
    font-size: 1.5rem;
    font-weight: 900;
    color: {BLACK};
    letter-spacing: -0.5px;
    font-family: 'IBM Plex Mono', monospace !important;
    line-height: 1;
}}
.mini-ind {{
    font-size: 0.55rem;
    font-weight: 900;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: {GRAY};
}}
.mini-delta-up   {{ font-size: 0.65rem; font-weight: 700; color: #16A34A; }}
.mini-delta-down {{ font-size: 0.65rem; font-weight: 700; color: {RED};   }}
.mini-delta-flat {{ font-size: 0.65rem; font-weight: 700; color: {LGRAY}; }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
COUNTRIES = {
    "México":    {"wb": "MX",  "iso3": "MEX", "flag": "🇲🇽"},
    "Brasil":    {"wb": "BR",  "iso3": "BRA", "flag": "🇧🇷"},
    "Argentina": {"wb": "AR",  "iso3": "ARG", "flag": "🇦🇷"},
    "Colombia":  {"wb": "CO",  "iso3": "COL", "flag": "🇨🇴"},
    "Chile":     {"wb": "CL",  "iso3": "CHL", "flag": "🇨🇱"},
    "Perú":      {"wb": "PE",  "iso3": "PER", "flag": "🇵🇪"},
}
INDICATORS = [
    "PIB (USD)", "PIB per cápita (USD)", "Población",
    "Gini", "Pobreza extrema (%)", "IDH", "Informalidad laboral (%)",
]
IND_SOURCE = {
    "PIB (USD)": "Banco Mundial", "PIB per cápita (USD)": "Banco Mundial",
    "Población": "Banco Mundial", "Gini": "Banco Mundial",
    "Pobreza extrema (%)": "Banco Mundial", "IDH": "PNUD · HDR 2023-24",
    "Informalidad laboral (%)": "OIT · SDG 8.3.1",
}
IND_DESC = {
    "PIB (USD)": "Producto Interno Bruto a precios corrientes en dólares",
    "PIB per cápita (USD)": "PIB dividido entre la población total estimada",
    "Población": "Población total estimada a mitad de año",
    "Gini": "Coeficiente de desigualdad · 0 = igualdad, 100 = desigualdad total",
    "Pobreza extrema (%)": "Población con menos de $2.15 USD/día (PPA 2017)",
    "IDH": "Índice compuesto de salud, educación e ingreso (0–1)",
    "Informalidad laboral (%)": "Proporción del empleo informal sobre el empleo total",
}
KEY_EVENTS = {2008: "Crisis\n2008", 2020: "COVID\n2020"}

# ─────────────────────────────────────────────────────────────────────────────
# LOGOS (base64 para embedding en HTML)
# ─────────────────────────────────────────────────────────────────────────────
_assets = Path(__file__).parent / "assets"

def _b64(path: Path) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

LOGO_ICON   = _b64(_assets / "BAEZTRIVE Logo.png")
LOGO_LETRAS = _b64(_assets / "BAEZTRIVE Logo Letras.png")

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def get_data(pais: str, indicador: str) -> pd.DataFrame:
    codes = COUNTRIES[pais]
    if indicador == "IDH":
        return fetch_hdi(codes["iso3"])
    elif indicador == "Informalidad laboral (%)":
        return fetch_informality(codes["iso3"])
    else:
        return fetch_world_bank(WB_INDICATORS[indicador], codes["wb"])


def fmt(val, ind):
    if pd.isna(val): return "—"
    if ind == "PIB (USD)":
        if val >= 1e12: return f"${val/1e12:.2f}T"
        if val >= 1e9:  return f"${val/1e9:.1f}B"
        return f"${val:,.0f}"
    if ind == "PIB per cápita (USD)": return f"${val:,.0f}"
    if ind == "Población":
        if val >= 1e6: return f"{val/1e6:.1f}M"
        return f"{val:,.0f}"
    if ind in ("Gini", "Pobreza extrema (%)", "Informalidad laboral (%)"): return f"{val:.1f}%"
    if ind == "IDH": return f"{val:.3f}"
    return f"{val:,.2f}"


def get_delta(serie: pd.Series):
    s = serie.dropna().sort_index()
    if len(s) < 2:
        return None, None
    latest, prev = s.iloc[-1], s.iloc[-2]
    pct = ((latest - prev) / abs(prev)) * 100 if prev != 0 else 0
    return pct, int(s.index[-2])


def delta_html(serie, prefix="stat-delta"):
    pct, yr = get_delta(serie)
    if pct is None:
        return f'<div class="{prefix}-flat">—</div>'
    arrow = "▲" if pct >= 0 else "▼"
    cls   = f"{prefix}-up" if pct >= 0 else f"{prefix}-down"
    return f'<div class="{cls}">{arrow} {abs(pct):.1f}% vs {yr}</div>'


def make_chart(dfs: dict, indicador: str, height=380) -> go.Figure:
    fig = go.Figure()
    all_years = set()
    for i, (pais, serie) in enumerate(dfs.items()):
        s     = serie.dropna().sort_index()
        all_years.update(s.index.tolist())
        color = PALETTE_LIGHT[i % len(PALETTE_LIGHT)]
        flag  = COUNTRIES[pais]["flag"]
        fig.add_trace(go.Scatter(
            x=s.index, y=s.values,
            name=f"{flag} {pais}",
            mode="lines+markers",
            line=dict(color=color, width=2.5, shape="spline", smoothing=0.5),
            marker=dict(size=4, color=color),
            hovertemplate=f"<b>{flag} {pais}</b> %{{x}}<br><b>%{{y:,.4~g}}</b><extra></extra>",
        ))
    for yr, label in KEY_EVENTS.items():
        if yr in all_years:
            fig.add_vline(
                x=yr, line=dict(color=LGRAY, width=1, dash="dot"),
                annotation_text=label, annotation_position="top",
                annotation_font=dict(size=8, color=GRAY),
                annotation_bgcolor=WHITE,
            )
    fig.update_layout(
        paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        font=dict(family="Gabarito, sans-serif", color=BLACK),
        margin=dict(l=0, r=0, t=20, b=0),
        height=height,
        xaxis=dict(
            showgrid=True, gridcolor="#F0EFE9", gridwidth=1,
            zeroline=False, tickfont=dict(size=11, color=GRAY),
            tickformat="d", linecolor=BORDER, showline=True,
        ),
        yaxis=dict(
            showgrid=True, gridcolor="#F0EFE9", gridwidth=1,
            zeroline=False, tickfont=dict(size=11, color=GRAY),
            linecolor=BORDER, showline=True,
        ),
        hovermode="x unified",
        hoverlabel=dict(bgcolor=WHITE, bordercolor=RED, font=dict(color=BLACK, size=12)),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="left", x=0, bgcolor="rgba(0,0,0,0)",
            font=dict(size=12, color=BLACK),
        ),
    )
    return fig


def make_mini_chart(serie: pd.Series, color=RED, height=90) -> go.Figure:
    s = serie.dropna().sort_index()
    fig = go.Figure()
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    fig.add_trace(go.Scatter(
        x=s.index, y=s.values,
        mode="lines",
        line=dict(color=color, width=2, shape="spline", smoothing=0.6),
        fill="tozeroy",
        fillcolor=f"rgba({r},{g},{b},0.06)",
        hovertemplate="%{x}: %{y:,.3~g}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor=WHITE, plot_bgcolor=WHITE,
        margin=dict(l=0, r=0, t=0, b=0), height=height,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, showline=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, showline=False),
        hovermode="x", hoverlabel=dict(bgcolor=WHITE, bordercolor=RED, font=dict(color=BLACK, size=10)),
        showlegend=False,
    )
    return fig

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:1.5rem 0 0.8rem;">
        <img src="data:image/png;base64,{LOGO_LETRAS}"
             style="width:100%;max-width:190px;display:block;">
        <div style="font-size:0.48rem;letter-spacing:3px;text-transform:uppercase;
                    color:{LGRAY};margin-top:0.5rem;">Data Studios · LATAM</div>
    </div>
    <hr style="border:none;border-top:1px solid {BORDER};margin:0 0 1.5rem;">
    """, unsafe_allow_html=True)

    vs_mode   = st.toggle("Vs Mode", value=False)
    pais_a    = st.selectbox("País", list(COUNTRIES.keys()), key="pa")
    pais_b    = st.selectbox("País B", list(COUNTRIES.keys()), index=1, key="pb") if vs_mode else None
    indicador = st.selectbox("Indicador", INDICATORS)

    st.markdown(f"""
    <div style="margin-top:1.5rem;padding:0.9rem;border:1px solid {BORDER};
                border-left:3px solid {RED};background:{PAPER};">
        <div style="font-size:0.55rem;letter-spacing:3px;text-transform:uppercase;
                    color:{GRAY};margin-bottom:0.5rem;font-weight:900;">Sobre este indicador</div>
        <div style="font-size:0.72rem;color:{BLACK};line-height:1.6;">{IND_DESC[indicador]}</div>
        <div class="src-tag" style="margin-top:0.8rem;">{IND_SOURCE[indicador]}</div>
    </div>
    """, unsafe_allow_html=True)

paises = [pais_a, pais_b] if vs_mode and pais_b else [pais_a]

with st.spinner(""):
    dfs = {}
    for p in paises:
        df = get_data(p, indicador)
        if not df.empty:
            dfs[p] = df.set_index("year")["value"]

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
t_explorar, t_perfil, t_rankings = st.tabs([
    "Explorar", "Perfil País", "Rankings",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB · EXPLORAR
# ══════════════════════════════════════════════════════════════════════════════
with t_explorar:
    if not dfs:
        st.warning("Sin datos disponibles.")
        st.stop()

    flag_str   = "  ".join(COUNTRIES[p]["flag"] for p in paises)
    label_pais = " vs ".join(paises)
    yr_latest  = max(int(s.dropna().sort_index().index[-1]) for s in dfs.values() if len(s.dropna()) > 0)

    # ── Header — mismo patrón que Perfil y Rankings ────────────────────────
    st.markdown(f"""
    <div style="position:relative;overflow:hidden;padding:2.5rem 0 1.5rem;
                border-bottom:2px solid {BLACK};margin-bottom:2rem;">

        <img src="data:image/png;base64,{LOGO_ICON}"
             style="position:absolute;top:1.5rem;right:0;width:72px;
                    opacity:0.9;border-radius:10px;">

        <div style="position:absolute;bottom:-0.5rem;left:-0.3rem;
                    font-size:9rem;font-weight:900;
                    color:rgba(249,43,43,0.05);
                    text-transform:uppercase;letter-spacing:-4px;line-height:1;
                    font-family:'IBM Plex Mono',monospace;white-space:nowrap;
                    pointer-events:none;">
            {indicador.upper().split("(")[0].strip()}
        </div>

        <div style="font-size:0.55rem;font-weight:900;letter-spacing:4px;
                    text-transform:uppercase;color:{RED};margin-bottom:0.4rem;">
            {flag_str} · {label_pais}
        </div>
        <div style="font-size:3rem;font-weight:900;color:{BLACK};
                    text-transform:uppercase;letter-spacing:-1px;line-height:1;">
            {indicador}
        </div>
        <div style="font-size:0.6rem;letter-spacing:2px;text-transform:uppercase;
                    color:{GRAY};margin-top:0.4rem;">
            {IND_SOURCE[indicador]} · Serie histórica 2000–{yr_latest}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stat strip — 4 cards por país ─────────────────────────────────────
    for i, (pais, serie) in enumerate(dfs.items()):
        s    = serie.dropna().sort_index()
        flag = COUNTRIES[pais]["flag"]
        val  = s.iloc[-1] if len(s) else None
        yr   = int(s.index[-1]) if len(s) else "—"
        pct, prev_yr = get_delta(s)
        mn, mx = s.min(), s.max()
        mn_yr  = int(s.idxmin()) if len(s) else "—"
        mx_yr  = int(s.idxmax()) if len(s) else "—"

        if pct is not None:
            arrow     = "▲" if pct >= 0 else "▼"
            d_cls     = "xp-delta-up" if pct >= 0 else "xp-delta-down"
            d_display = f'<span class="{d_cls}">{arrow} {abs(pct):.1f}%</span>'
            d_sub     = f"vs {prev_yr}"
        else:
            d_display = '<span class="xp-delta-flat">—</span>'
            d_sub     = ""

        if len(dfs) > 1:
            border_t = "none" if i == 0 else f"1px solid {BORDER}"
            st.markdown(f"""
            <div style="font-size:0.55rem;font-weight:900;letter-spacing:4px;
                        text-transform:uppercase;color:{GRAY};
                        padding:{('1.2rem' if i > 0 else '0')} 0 0.6rem;
                        border-top:{border_t};">
                {flag} {pais.upper()}
            </div>
            """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4, gap="small")
        with c1:
            st.markdown(f"""
            <div class="xp-card accent">
                <div class="xp-label">Último dato · {yr}</div>
                <div class="xp-value">{fmt(val, indicador) if val is not None else '—'}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="xp-card">
                <div class="xp-label">Variación anual</div>
                <div class="xp-value">{d_display}</div>
                <div class="xp-sub">{d_sub}</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="xp-card">
                <div class="xp-label">Mínimo · {mn_yr}</div>
                <div class="xp-value">{fmt(mn, indicador)}</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="xp-card">
                <div class="xp-label">Máximo · {mx_yr}</div>
                <div class="xp-value">{fmt(mx, indicador)}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Chart ─────────────────────────────────────────────────────────────
    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="sec-label">Evolución histórica</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:{WHITE};border:1px solid {BORDER};padding:1.5rem 1.5rem 0.5rem;">', unsafe_allow_html=True)
    fig = make_chart(dfs, indicador, height=400)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Data table ────────────────────────────────────────────────────────
    st.markdown("<hr class='div-line'>", unsafe_allow_html=True)
    st.markdown('<div class="sec-label">Datos históricos</div>', unsafe_allow_html=True)

    combined = pd.DataFrame(dfs).sort_index(ascending=False)
    combined.index.name = "Año"

    dl_col, _ = st.columns([1, 6])
    with dl_col:
        st.download_button(
            "↓ Descargar CSV",
            data=combined.to_csv().encode("utf-8"),
            file_name=f"baeztrive_{indicador.lower().replace(' ','_').replace('/','')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    st.dataframe(
        combined.style.format(lambda v: fmt(v, indicador)),
        use_container_width=True, height=260,
    )

    st.markdown(f"""
    <div class="pg-footer">
        <div class="pg-footer-brand"><span>BAEZTRIVE</span> Data Studios</div>
        <div class="pg-footer-src">Fuente: {IND_SOURCE[indicador]}</div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB · PERFIL PAÍS
# ══════════════════════════════════════════════════════════════════════════════
with t_perfil:
    flag = COUNTRIES[pais_a]["flag"]

    # Big typographic country header
    st.markdown(f"""
    <div style="position:relative;overflow:hidden;padding:2.5rem 0 1.5rem;
                border-bottom:2px solid {BLACK};margin-bottom:2rem;">
        <div style="position:absolute;top:-1rem;left:-0.5rem;
                    font-size:9rem;font-weight:900;color:rgba(249,43,43,0.06);
                    text-transform:uppercase;letter-spacing:-4px;line-height:1;
                    font-family:'IBM Plex Mono',monospace;white-space:nowrap;
                    pointer-events:none;">{pais_a.upper()}</div>
        <div style="font-size:0.55rem;font-weight:900;letter-spacing:4px;
                    text-transform:uppercase;color:{RED};margin-bottom:0.4rem;">
            {flag} Perfil completo
        </div>
        <div style="font-size:3rem;font-weight:900;color:{BLACK};
                    text-transform:uppercase;letter-spacing:-1px;line-height:1;">
            {pais_a}
        </div>
        <div style="font-size:0.6rem;letter-spacing:2px;text-transform:uppercase;
                    color:{GRAY};margin-top:0.4rem;">
            Todos los indicadores · 2000 – 2023
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner(""):
        profile_data = {}
        for ind in INDICATORS:
            df = get_data(pais_a, ind)
            if not df.empty:
                profile_data[ind] = df.set_index("year")["value"]

    rows = [INDICATORS[i:i+2] for i in range(0, len(INDICATORS), 2)]
    for row in rows:
        cols = st.columns(len(row), gap="medium")
        for ci, ind in enumerate(row):
            if ind not in profile_data:
                continue
            s    = profile_data[ind].dropna().sort_index()
            val  = s.iloc[-1] if len(s) else None
            yr   = int(s.index[-1]) if len(s) else "—"
            pct, prev_yr = get_delta(s)

            if pct is not None:
                arrow = "▲" if pct >= 0 else "▼"
                dcls  = "mini-delta-up" if pct >= 0 else "mini-delta-down"
                d_html = f'<span class="{dcls}">{arrow} {abs(pct):.1f}%</span>'
            else:
                d_html = f'<span class="mini-delta-flat">—</span>'

            with cols[ci]:
                st.markdown(f"""
                <div class="mini-card">
                    <div class="mini-card-top">
                        <div>
                            <div class="mini-ind">{ind}</div>
                            <div class="mini-val">{fmt(val, ind) if val is not None else '—'}</div>
                            <div style="margin-top:0.2rem;font-size:0.6rem;color:{GRAY};">
                                {yr} · {d_html}
                            </div>
                        </div>
                        <div class="src-tag">{IND_SOURCE[ind].split('·')[0].strip()}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                fig_mini = make_mini_chart(s, color=RED if ci == 0 else BLACK, height=88)
                st.plotly_chart(
                    fig_mini, use_container_width=True,
                    config={"displayModeBar": False},
                    key=f"mini_{pais_a}_{ind}",
                )

    st.markdown(f"""
    <div class="pg-footer">
        <div class="pg-footer-brand"><span>BAEZTRIVE</span> Data Studios</div>
        <div class="pg-footer-src">{flag} {pais_a} · Banco Mundial · PNUD · OIT</div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB · RANKINGS
# ══════════════════════════════════════════════════════════════════════════════
with t_rankings:
    st.markdown(f"""
    <div style="position:relative;overflow:hidden;padding:2.5rem 0 1.5rem;
                border-bottom:2px solid {BLACK};margin-bottom:2rem;">
        <div style="font-size:0.55rem;font-weight:900;letter-spacing:4px;
                    text-transform:uppercase;color:{RED};margin-bottom:0.4rem;">
            6 países · LATAM
        </div>
        <div style="font-size:3rem;font-weight:900;color:{BLACK};
                    text-transform:uppercase;letter-spacing:-1px;line-height:1;">
            {indicador}
        </div>
        <div style="font-size:0.6rem;letter-spacing:2px;text-transform:uppercase;
                    color:{GRAY};margin-top:0.4rem;">
            Ranking regional · último dato disponible por país
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner(""):
        rank_rows = []
        for p in COUNTRIES:
            df = get_data(p, indicador)
            if not df.empty:
                s = df.set_index("year")["value"].dropna().sort_index()
                if len(s):
                    rank_rows.append({
                        "pais": p,
                        "flag": COUNTRIES[p]["flag"],
                        "value": s.iloc[-1],
                        "year": int(s.index[-1]),
                    })

    if rank_rows:
        rank_df = pd.DataFrame(rank_rows).sort_values("value", ascending=False).reset_index(drop=True)
        max_val = rank_df["value"].max()

        # Typographic rank list
        st.markdown(f'<div style="background:{WHITE};border:1px solid {BORDER};padding:0.5rem 1.5rem;">', unsafe_allow_html=True)
        for i, row in rank_df.iterrows():
            pct_bar = (row["value"] / max_val) * 100 if max_val > 0 else 0
            is_leader = i == 0
            fill_class = "rank-bar-fill leader" if is_leader else "rank-bar-fill"
            val_class  = "rank-value leader" if is_leader else "rank-value"
            num_style  = f"color:{RED};font-weight:900;" if is_leader else ""
            st.markdown(f"""
            <div class="rank-row">
                <div class="rank-num" style="{num_style}">0{i+1}</div>
                <div class="rank-country">{row['flag']} {row['pais']}</div>
                <div class="rank-bar-track">
                    <div class="{fill_class}" style="width:{pct_bar:.1f}%;"></div>
                </div>
                <div class="{val_class}">{fmt(row['value'], indicador)}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

        # Summary cards
        leader = rank_df.iloc[0]
        last   = rank_df.iloc[-1]
        gap    = ((leader["value"] - last["value"]) / abs(last["value"])) * 100 if last["value"] != 0 else 0

        c1, c2, c3 = st.columns(3, gap="medium")
        with c1:
            st.markdown(f"""
            <div class="stat-card red-top">
                <div class="stat-label">{COUNTRIES[leader['pais']]['flag']} Líder regional</div>
                <div class="stat-value">{leader['pais']}</div>
                <div class="stat-delta-up">{fmt(leader['value'], indicador)} · {leader['year']}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">{COUNTRIES[last['pais']]['flag']} Rezagado</div>
                <div class="stat-value">{last['pais']}</div>
                <div class="stat-delta-down">{fmt(last['value'], indicador)} · {last['year']}</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Brecha líder / rezagado</div>
                <div class="stat-value">{abs(gap):.0f}%</div>
                <div class="stat-delta-flat">diferencia relativa</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="pg-footer">
        <div class="pg-footer-brand"><span>BAEZTRIVE</span> Data Studios</div>
        <div class="pg-footer-src">Fuente: {IND_SOURCE[indicador]}</div>
    </div>
    """, unsafe_allow_html=True)
