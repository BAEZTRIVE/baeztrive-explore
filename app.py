import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
# DESIGN SYSTEM
# ─────────────────────────────────────────────────────────────────────────────
BG       = "#080808"
SURFACE  = "#0E0E0E"
SURFACE2 = "#141414"
BORDER   = "#1C1C1C"
RED      = "#F92B2B"
WHITE    = "#F0F0F0"
MUTED    = "#3A3A3A"
DIM      = "#222222"
GREEN    = "#22C55E"
ORANGE   = "#F97316"
BLUE     = "#60A5FA"
PURPLE   = "#A78BFA"

PALETTE  = [RED, WHITE, ORANGE, BLUE, GREEN, PURPLE]

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Gabarito:wght@400;700;900&display=swap');

*, *::before, *::after {{ font-family: 'Gabarito', sans-serif !important; }}

/* ── RESET BACKGROUND ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="block-container"],
[data-testid="stMainBlockContainer"] {{
    background-color: {BG} !important;
    color: {WHITE} !important;
    padding-top: 0 !important;
}}

[data-testid="stHeader"] {{
    background-color: {BG} !important;
    border-bottom: 1px solid {BORDER};
}}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {{
    background-color: {SURFACE} !important;
    border-right: 1px solid {BORDER} !important;
}}
[data-testid="stSidebar"] > div {{ padding-top: 0 !important; }}

/* ── TABS ── */
[data-testid="stTabs"] [role="tablist"] {{
    background: {SURFACE} !important;
    border-bottom: 1px solid {BORDER} !important;
    gap: 0 !important;
    padding: 0 !important;
}}
[data-testid="stTabs"] button[role="tab"] {{
    background: transparent !important;
    color: {MUTED} !important;
    border: none !important;
    border-bottom: 3px solid transparent !important;
    border-radius: 0 !important;
    font-size: 0.65rem !important;
    font-weight: 900 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    padding: 1rem 2rem !important;
    transition: all 0.2s !important;
}}
[data-testid="stTabs"] button[role="tab"]:hover {{
    color: {WHITE} !important;
    background: {SURFACE2} !important;
}}
[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {RED} !important;
    border-bottom: 3px solid {RED} !important;
    background: {BG} !important;
}}
[data-testid="stTabPanel"] {{
    background: {BG} !important;
    padding: 2rem 0 !important;
}}

/* ── SELECTBOX / RADIO ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stRadio"] > div {{
    background: {SURFACE2} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 2px !important;
}}
[data-testid="stSelectbox"] label,
[data-testid="stRadio"] label,
[data-testid="stRadio"] p {{
    font-size: 0.6rem !important;
    font-weight: 900 !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    color: {MUTED} !important;
}}

/* ── SPINNER ── */
[data-testid="stSpinner"] p {{
    color: {MUTED} !important;
    font-size: 0.6rem !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
}}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] {{
    border: 1px solid {BORDER} !important;
}}
.stDataFrame thead th {{
    background: {SURFACE2} !important;
    color: {MUTED} !important;
    font-size: 0.6rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}}

/* ── SCROLLBAR ── */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: {BG}; }}
::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 2px; }}
::-webkit-scrollbar-thumb:hover {{ background: {RED}; }}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, [data-testid="stDecoration"] {{ display: none !important; }}

/* ── METRIC CARD ── */
.bx-card {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-top: 2px solid {RED};
    padding: 1.2rem 1.4rem 1rem;
}}
.bx-label {{
    font-size: 0.58rem;
    font-weight: 900;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: {MUTED};
    margin-bottom: 0.4rem;
}}
.bx-value {{
    font-size: 2.2rem;
    font-weight: 900;
    color: {WHITE};
    line-height: 1;
    letter-spacing: -1px;
}}
.bx-delta-up   {{ font-size: 0.75rem; font-weight: 700; color: {GREEN};  margin-top: 0.35rem; }}
.bx-delta-down {{ font-size: 0.75rem; font-weight: 700; color: {RED};    margin-top: 0.35rem; }}
.bx-delta-flat {{ font-size: 0.75rem; font-weight: 700; color: {MUTED};  margin-top: 0.35rem; }}

/* ── HERO ── */
.bx-hero-kicker {{
    font-size: 0.6rem;
    font-weight: 900;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: {RED};
    margin-bottom: 0.6rem;
}}
.bx-hero-title {{
    font-size: clamp(2rem, 5vw, 3.5rem);
    font-weight: 900;
    color: {WHITE};
    text-transform: uppercase;
    letter-spacing: -1px;
    line-height: 1;
    margin-bottom: 0.2rem;
}}
.bx-hero-sub {{
    font-size: 0.65rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: {MUTED};
}}
.bx-divider {{
    border: none;
    border-top: 1px solid {BORDER};
    margin: 1.5rem 0;
}}
.bx-section-label {{
    font-size: 0.6rem;
    font-weight: 900;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: {MUTED};
    margin-bottom: 1rem;
}}
.bx-footer {{
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid {BORDER};
    display: flex;
    justify-content: space-between;
    align-items: center;
}}
.bx-footer-l {{ font-size: 0.58rem; letter-spacing: 3px; text-transform: uppercase; color: {DIM}; font-weight: 900; }}
.bx-footer-r {{ font-size: 0.58rem; letter-spacing: 2px; text-transform: uppercase; color: {DIM}; }}

/* ── PROFILE MINI CARD ── */
.bx-mini-label {{
    font-size: 0.55rem;
    font-weight: 900;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: {MUTED};
}}
.bx-mini-value {{
    font-size: 1.4rem;
    font-weight: 900;
    color: {WHITE};
    letter-spacing: -0.5px;
    line-height: 1;
}}
.bx-mini-delta-up   {{ font-size: 0.65rem; font-weight: 700; color: {GREEN}; }}
.bx-mini-delta-down {{ font-size: 0.65rem; font-weight: 700; color: {RED};   }}
.bx-mini-delta-flat {{ font-size: 0.65rem; font-weight: 700; color: {MUTED}; }}
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
    "PIB (USD)",
    "PIB per cápita (USD)",
    "Población",
    "Gini",
    "Pobreza extrema (%)",
    "IDH",
    "Informalidad laboral (%)",
]

INDICATOR_SOURCE = {
    "PIB (USD)":              "Banco Mundial",
    "PIB per cápita (USD)":   "Banco Mundial",
    "Población":              "Banco Mundial",
    "Gini":                   "Banco Mundial",
    "Pobreza extrema (%)":    "Banco Mundial",
    "IDH":                    "PNUD · HDR 2023–24",
    "Informalidad laboral (%)": "OIT · SDG 8.3.1",
}

INDICATOR_DESC = {
    "PIB (USD)":              "Producto Interno Bruto a precios corrientes en dólares",
    "PIB per cápita (USD)":   "PIB dividido entre la población total estimada",
    "Población":              "Población total estimada a mitad de año",
    "Gini":                   "Coeficiente de desigualdad (0 = perfecta igualdad)",
    "Pobreza extrema (%)":    "% de la población con menos de $2.15 USD/día (PPA 2017)",
    "IDH":                    "Índice compuesto de salud, educación e ingreso (0–1)",
    "Informalidad laboral (%)": "Proporción del empleo informal sobre el empleo total",
}

KEY_EVENTS = {
    2008: "Crisis\nfinanciera",
    2020: "COVID-19",
}

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
    if pd.isna(val):
        return "—"
    if ind == "PIB (USD)":
        if val >= 1e12: return f"${val/1e12:.2f}T"
        if val >= 1e9:  return f"${val/1e9:.1f}B"
        return f"${val:,.0f}"
    if ind == "PIB per cápita (USD)":
        return f"${val:,.0f}"
    if ind == "Población":
        if val >= 1e6: return f"{val/1e6:.1f}M"
        return f"{val:,.0f}"
    if ind in ("Gini", "Pobreza extrema (%)", "Informalidad laboral (%)"):
        return f"{val:.1f}%"
    if ind == "IDH":
        return f"{val:.3f}"
    return f"{val:,.2f}"


def delta_html(serie: pd.Series, cls_prefix: str = "bx-delta"):
    s = serie.dropna()
    if len(s) < 2:
        return f'<div class="{cls_prefix}-flat">— sin dato previo</div>'
    latest, prev = s.iloc[-1], s.iloc[-2]
    pct = ((latest - prev) / abs(prev)) * 100 if prev != 0 else 0
    arrow = "▲" if pct >= 0 else "▼"
    cls   = f"{cls_prefix}-up" if pct >= 0 else f"{cls_prefix}-down"
    return f'<div class="{cls}">{arrow} {abs(pct):.1f}% vs {s.index[-2]}</div>'


def base_layout(height=420):
    return dict(
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(family="Gabarito, sans-serif", color=WHITE),
        margin=dict(l=0, r=0, t=10, b=0),
        height=height,
        xaxis=dict(
            showgrid=True, gridcolor=SURFACE2, gridwidth=1,
            zeroline=False, tickfont=dict(size=11, color=MUTED),
            tickformat="d", linecolor=BORDER,
        ),
        yaxis=dict(
            showgrid=True, gridcolor=SURFACE2, gridwidth=1,
            zeroline=False, tickfont=dict(size=11, color=MUTED),
            linecolor=BORDER,
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=SURFACE2, bordercolor=RED,
            font=dict(color=WHITE, size=12),
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="left", x=0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=13, color=WHITE),
        ),
    )


def add_event_lines(fig, years):
    for yr, label in KEY_EVENTS.items():
        if yr in years:
            fig.add_vline(
                x=yr,
                line=dict(color=MUTED, width=1, dash="dot"),
                annotation_text=label,
                annotation_position="top",
                annotation_font=dict(size=9, color=MUTED),
                annotation_bgcolor=BG,
            )


def area_chart(dfs: dict, indicador: str, height=420) -> go.Figure:
    fig = go.Figure()
    all_years = set()
    for i, (pais, serie) in enumerate(dfs.items()):
        s = serie.dropna().sort_index()
        all_years.update(s.index.tolist())
        color = PALETTE[i % len(PALETTE)]
        flag  = COUNTRIES[pais]["flag"]
        fill_color = color.replace("#", "").strip()
        r, g, b = int(fill_color[0:2], 16), int(fill_color[2:4], 16), int(fill_color[4:6], 16)
        fig.add_trace(go.Scatter(
            x=s.index, y=s.values,
            name=f"{flag} {pais}",
            mode="lines",
            line=dict(color=color, width=2.5, shape="spline", smoothing=0.6),
            fill="tozeroy" if len(dfs) == 1 else "none",
            fillcolor=f"rgba({r},{g},{b},0.07)",
            hovertemplate=f"<b>{flag} {pais}</b><br>%{{x}}: %{{y:,.3~g}}<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=[s.index[-1]], y=[s.values[-1]],
            mode="markers+text",
            marker=dict(size=8, color=color, symbol="circle"),
            text=[f" {fmt(s.values[-1], indicador)}"],
            textposition="middle right",
            textfont=dict(size=11, color=color, family="Gabarito"),
            showlegend=False,
            hoverinfo="skip",
        ))
    add_event_lines(fig, all_years)
    fig.update_layout(**base_layout(height))
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:1.5rem 0 1rem 0;border-bottom:1px solid {BORDER};margin-bottom:1.5rem;">
        <div style="font-size:0.55rem;letter-spacing:5px;text-transform:uppercase;
                    color:{RED};font-weight:900;margin-bottom:0.2rem;">
            BAEZTRIVE
        </div>
        <div style="font-size:1.6rem;font-weight:900;color:{WHITE};
                    text-transform:uppercase;letter-spacing:-0.5px;line-height:1;">
            Explore
        </div>
        <div style="font-size:0.55rem;letter-spacing:3px;color:{MUTED};
                    text-transform:uppercase;margin-top:0.3rem;">
            Data Studios · LATAM
        </div>
    </div>
    """, unsafe_allow_html=True)

    vs_mode  = st.toggle("Vs Mode", value=False)
    pais_a   = st.selectbox("País", list(COUNTRIES.keys()), key="pais_a")
    if vs_mode:
        pais_b = st.selectbox("País B", list(COUNTRIES.keys()), index=1, key="pais_b")
    indicador = st.selectbox("Indicador", INDICATORS)

    st.markdown(f"""
    <div style="margin-top:1.5rem;padding:0.9rem;
                background:{SURFACE2};border-left:2px solid {RED};">
        <div style="font-size:0.55rem;letter-spacing:3px;text-transform:uppercase;
                    color:{MUTED};margin-bottom:0.4rem;font-weight:900;">Descripción</div>
        <div style="font-size:0.7rem;color:#666;line-height:1.6;">
            {INDICATOR_DESC[indicador]}
        </div>
        <div style="font-size:0.55rem;letter-spacing:2px;text-transform:uppercase;
                    color:{RED};margin-top:0.6rem;font-weight:900;">
            {INDICATOR_SOURCE[indicador]}
        </div>
    </div>
    """, unsafe_allow_html=True)

paises = [pais_a, pais_b] if vs_mode else [pais_a]

# ─────────────────────────────────────────────────────────────────────────────
# FETCH DATA
# ─────────────────────────────────────────────────────────────────────────────
with st.spinner("Consultando fuentes..."):
    dfs = {}
    for p in paises:
        df = get_data(p, indicador)
        if not df.empty:
            dfs[p] = df.set_index("year")["value"]

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_explorar, tab_perfil, tab_rankings = st.tabs([
    "⬛  Explorar",
    "◻  Perfil País",
    "▶  Rankings",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 · EXPLORAR
# ══════════════════════════════════════════════════════════════════════════════
with tab_explorar:
    flag_str    = "  ".join(COUNTRIES[p]["flag"] for p in paises)
    label_pais  = " vs ".join(paises)

    st.markdown(f"""
    <div style="padding:0 0 1.5rem 0;">
        <div class="bx-hero-kicker">{flag_str} &nbsp; {label_pais.upper()}</div>
        <div class="bx-hero-title">{indicador}</div>
        <div class="bx-hero-sub">{INDICATOR_SOURCE[indicador]}</div>
    </div>
    <hr class="bx-divider">
    """, unsafe_allow_html=True)

    if not dfs:
        st.markdown(f"""
        <div style="padding:4rem;text-align:center;border:1px solid {BORDER};">
            <div style="font-size:0.7rem;letter-spacing:3px;text-transform:uppercase;color:{MUTED};">
                Sin datos disponibles para esta selección
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # Metric cards
    cols = st.columns(len(dfs))
    for i, (pais, serie) in enumerate(dfs.items()):
        s    = serie.dropna().sort_index()
        last = s.iloc[-1] if len(s) else None
        yr   = int(s.index[-1]) if len(s) else "—"
        flag = COUNTRIES[pais]["flag"]
        with cols[i]:
            st.markdown(f"""
            <div class="bx-card">
                <div class="bx-label">{flag} {pais} · {yr}</div>
                <div class="bx-value">{fmt(last, indicador) if last is not None else '—'}</div>
                {delta_html(s, 'bx-delta')}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # Main chart
    fig = area_chart(dfs, indicador)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Download + table
    st.markdown("<hr class='bx-divider'>", unsafe_allow_html=True)
    combined = pd.DataFrame(dfs).sort_index(ascending=False)
    combined.index.name = "Año"

    dl_col, _ = st.columns([1, 5])
    with dl_col:
        csv = combined.to_csv().encode("utf-8")
        st.download_button(
            label="↓ Descargar CSV",
            data=csv,
            file_name=f"baeztrive_{indicador.lower().replace(' ','_')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.markdown(f'<div class="bx-section-label">Datos históricos</div>', unsafe_allow_html=True)
    st.dataframe(
        combined.style.format(lambda v: fmt(v, indicador)),
        use_container_width=True,
        height=260,
    )

    st.markdown(f"""
    <div class="bx-footer">
        <div class="bx-footer-l">BAEZTRIVE Data Studios</div>
        <div class="bx-footer-r">Fuentes: {INDICATOR_SOURCE[indicador]}</div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 · PERFIL PAÍS
# ══════════════════════════════════════════════════════════════════════════════
with tab_perfil:
    flag = COUNTRIES[pais_a]["flag"]

    st.markdown(f"""
    <div style="padding:0 0 1.5rem 0;">
        <div class="bx-hero-kicker">{flag} Perfil completo</div>
        <div class="bx-hero-title">{pais_a}</div>
        <div class="bx-hero-sub">Todos los indicadores · 2000–2023</div>
    </div>
    <hr class="bx-divider">
    """, unsafe_allow_html=True)

    with st.spinner("Cargando perfil completo..."):
        profile_data = {}
        for ind in INDICATORS:
            df = get_data(pais_a, ind)
            if not df.empty:
                profile_data[ind] = df.set_index("year")["value"]

    rows = [INDICATORS[i:i+2] for i in range(0, len(INDICATORS), 2)]

    for row in rows:
        cols = st.columns(len(row))
        for ci, ind in enumerate(row):
            with cols[ci]:
                if ind not in profile_data:
                    continue
                s    = profile_data[ind].dropna().sort_index()
                last = s.iloc[-1] if len(s) else None
                yr   = int(s.index[-1]) if len(s) else "—"

                # Mini chart
                fig_mini = go.Figure()
                fig_mini.add_trace(go.Scatter(
                    x=s.index, y=s.values,
                    mode="lines",
                    line=dict(color=RED, width=2, shape="spline", smoothing=0.6),
                    fill="tozeroy",
                    fillcolor=f"rgba(249,43,43,0.07)",
                    hovertemplate="%{x}: %{y:,.3~g}<extra></extra>",
                ))
                fig_mini.update_layout(
                    paper_bgcolor=SURFACE,
                    plot_bgcolor=SURFACE,
                    margin=dict(l=0, r=0, t=0, b=0),
                    height=130,
                    xaxis=dict(
                        showgrid=False, zeroline=False,
                        tickfont=dict(size=9, color=MUTED),
                        tickformat="d", showticklabels=True,
                        linecolor=BORDER,
                    ),
                    yaxis=dict(
                        showgrid=False, zeroline=False,
                        showticklabels=False, linecolor=BORDER,
                    ),
                    hovermode="x",
                    hoverlabel=dict(bgcolor=SURFACE2, bordercolor=RED, font=dict(color=WHITE, size=11)),
                    showlegend=False,
                )

                dlt = delta_html(s, "bx-mini-delta")
                st.markdown(f"""
                <div style="background:{SURFACE};border:1px solid {BORDER};
                            border-top:2px solid {RED};padding:1rem 1rem 0.5rem;
                            margin-bottom:0.8rem;">
                    <div class="bx-mini-label">{ind}</div>
                    <div class="bx-mini-value" style="margin:0.3rem 0;">
                        {fmt(last, ind) if last is not None else '—'}
                    </div>
                    {dlt}
                </div>
                """, unsafe_allow_html=True)
                st.plotly_chart(
                    fig_mini, use_container_width=True,
                    config={"displayModeBar": False},
                    key=f"mini_{pais_a}_{ind}",
                )

    st.markdown(f"""
    <div class="bx-footer">
        <div class="bx-footer-l">BAEZTRIVE Data Studios</div>
        <div class="bx-footer-r">{flag} {pais_a} · Fuentes: Banco Mundial · PNUD · OIT</div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 · RANKINGS
# ══════════════════════════════════════════════════════════════════════════════
with tab_rankings:
    st.markdown(f"""
    <div style="padding:0 0 1.5rem 0;">
        <div class="bx-hero-kicker">6 países · LATAM</div>
        <div class="bx-hero-title">{indicador}</div>
        <div class="bx-hero-sub">Ranking regional · último dato disponible</div>
    </div>
    <hr class="bx-divider">
    """, unsafe_allow_html=True)

    with st.spinner("Calculando ranking..."):
        rank_data = {}
        for p in COUNTRIES:
            df = get_data(p, indicador)
            if not df.empty:
                s = df.set_index("year")["value"].dropna().sort_index()
                if len(s):
                    rank_data[p] = {"value": s.iloc[-1], "year": int(s.index[-1])}

    if rank_data:
        rank_df = pd.DataFrame(rank_data).T.sort_values("value", ascending=True)
        rank_df["flag"] = [COUNTRIES[p]["flag"] for p in rank_df.index]
        rank_df["label"] = [f'{COUNTRIES[p]["flag"]} {p}' for p in rank_df.index]
        rank_df["fmt"]   = [fmt(v, indicador) for v in rank_df["value"]]
        rank_df["color"] = [RED if p == rank_df.index[-1] else MUTED for p in rank_df.index]

        fig_rank = go.Figure()

        # Background bars (track)
        fig_rank.add_trace(go.Bar(
            y=rank_df["label"],
            x=[rank_df["value"].max() * 1.15] * len(rank_df),
            orientation="h",
            marker=dict(color=SURFACE2),
            showlegend=False,
            hoverinfo="skip",
        ))

        # Value bars
        fig_rank.add_trace(go.Bar(
            y=rank_df["label"],
            x=rank_df["value"],
            orientation="h",
            marker=dict(
                color=rank_df["color"].tolist(),
                line=dict(width=0),
            ),
            text=rank_df["fmt"],
            textposition="outside",
            textfont=dict(size=13, color=WHITE, family="Gabarito"),
            hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>",
            showlegend=False,
        ))

        fig_rank.update_layout(
            paper_bgcolor=BG, plot_bgcolor=BG,
            barmode="overlay",
            margin=dict(l=0, r=80, t=10, b=0),
            height=360,
            font=dict(family="Gabarito, sans-serif", color=WHITE),
            xaxis=dict(
                showgrid=False, zeroline=False,
                showticklabels=False, linecolor=BORDER,
            ),
            yaxis=dict(
                tickfont=dict(size=14, color=WHITE),
                linecolor=BORDER, gridcolor=BORDER,
            ),
            hoverlabel=dict(bgcolor=SURFACE2, bordercolor=RED, font=dict(color=WHITE, size=12)),
        )

        st.plotly_chart(fig_rank, use_container_width=True, config={"displayModeBar": False})

        # Winner callout
        winner = rank_df.index[-1]
        winner_val = rank_df.loc[winner, "value"]
        winner_yr  = int(rank_df.loc[winner, "year"])
        loser      = rank_df.index[0]
        loser_val  = rank_df.loc[loser, "value"]
        gap_pct    = ((winner_val - loser_val) / abs(loser_val)) * 100 if loser_val != 0 else 0

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="bx-card">
                <div class="bx-label">{COUNTRIES[winner]["flag"]} Líder regional</div>
                <div class="bx-value">{winner}</div>
                <div class="bx-delta-up">{fmt(winner_val, indicador)} · {winner_yr}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="bx-card">
                <div class="bx-label">{COUNTRIES[loser]["flag"]} Rezagado</div>
                <div class="bx-value">{loser}</div>
                <div class="bx-delta-down">{fmt(loser_val, indicador)} · {int(rank_df.loc[loser,'year'])}</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="bx-card">
                <div class="bx-label">Brecha líder vs rezagado</div>
                <div class="bx-value">{abs(gap_pct):.0f}%</div>
                <div class="bx-delta-flat">diferencia relativa</div>
            </div>
            """, unsafe_allow_html=True)

        # Ranking table
        st.markdown("<hr class='bx-divider'>", unsafe_allow_html=True)
        st.markdown('<div class="bx-section-label">Tabla de ranking</div>', unsafe_allow_html=True)
        display_rank = rank_df[["flag", "fmt", "year"]].copy()
        display_rank.columns = ["", indicador, "Año"]
        display_rank.index = range(len(display_rank) - 1, -1, -1)
        display_rank.index = display_rank.index + 1
        display_rank.index.name = "#"
        st.dataframe(display_rank[::-1], use_container_width=True, height=280)

    st.markdown(f"""
    <div class="bx-footer">
        <div class="bx-footer-l">BAEZTRIVE Data Studios</div>
        <div class="bx-footer-r">Fuente: {INDICATOR_SOURCE[indicador]}</div>
    </div>
    """, unsafe_allow_html=True)
