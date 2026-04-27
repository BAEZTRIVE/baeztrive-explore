import streamlit as st
import pandas as pd
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "pipeline"))

from world_bank import fetch_world_bank, WB_INDICATORS
from hdi import fetch_hdi
from ilo import fetch_informality

st.set_page_config(page_title="BAEZTRIVE Explore", layout="wide")
# Inyectar fuente y estilos BAEZTRIVE
st.markdown("""
    <style>
       @import url('https://fonts.googleapis.com/css2?family=Gabarito:wght@400;700;900&display=swap');

* { font-family: 'Gabarito', sans-serif !important; }

/* ---- FONDO SIEMPRE NEGRO ---- */
html, body, 
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="block-container"] {
    background-color: #0C0C0C !important;
    color: #F4F4F4 !important;
}

[data-testid="stHeader"] {
    background-color: #0C0C0C !important;
}

/* ---- TIPOGRAFÍA ---- */
h1 {
    font-size: 3.5rem !important;
    font-weight: 900 !important;
    letter-spacing: -1px;
    color: #F92B2B !important;
    text-transform: uppercase;
    border-bottom: 3px solid #F92B2B;
    padding-bottom: 0.3rem;
}

h2, h3 {
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ---- CONTROLES ---- */
div[data-testid="stSelectbox"],
div[data-testid="stRadio"] {
    background-color: #1A1A1A !important;
    border: 1px solid #F92B2B;
    border-radius: 0px !important;
    padding: 0.5rem;
}

.stRadio label {
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 2px;
}

/* ---- TAG ---- */
.baeztrive-tag {
    font-size: 0.7rem;
    color: #F92B2B;
    text-transform: uppercase;
    letter-spacing: 4px;
    font-weight: 700;
}

/* ---- DATAFRAME ---- */
.stDataFrame {
    border: 1px solid #F92B2B !important;
}
    </style>
""", unsafe_allow_html=True)
st.title("BAEZTRIVE Explore 🔴")
st.markdown('<p class="baeztrive-tag">⬛ BAEZTRIVE Data Studios — Exploración de datos de desarrollo y desigualdad en LATAM</p>', unsafe_allow_html=True)

# Configuración de países
COUNTRIES = {
    "México": {"wb": "MX", "iso3": "MEX"},
    "Brasil": {"wb": "BR", "iso3": "BRA"},
    "Argentina": {"wb": "AR", "iso3": "ARG"},
}

# Modo
modo = st.radio("Modo", ["País individual", "Vs Mode"], horizontal=True)

if modo == "País individual":
    pais = st.selectbox("Selecciona un país", list(COUNTRIES.keys()))
    paises_seleccionados = [pais]
else:
    col1, col2 = st.columns(2)
    with col1:
        pais1 = st.selectbox("País 1", list(COUNTRIES.keys()), index=0)
    with col2:
        pais2 = st.selectbox("País 2", list(COUNTRIES.keys()), index=1)
    paises_seleccionados = [pais1, pais2]

# Selector de indicador
indicador = st.selectbox("Selecciona un indicador", [
    "PIB (USD)",
    "PIB per cápita (USD)",
    "Población",
    "Gini",
    "Pobreza extrema (%)",
    "IDH",
    "Informalidad laboral (%)"
])

# Jalar datos
def get_data(pais, indicador):
    codes = COUNTRIES[pais]
    if indicador == "IDH":
        return fetch_hdi(codes["iso3"])
    elif indicador == "Informalidad laboral (%)":
        return fetch_informality(codes["iso3"])
    else:
        return fetch_world_bank(WB_INDICATORS[indicador], codes["wb"])

with st.spinner("Jalando datos..."):
    dfs = {}
    for pais in paises_seleccionados:
        df = get_data(pais, indicador)
        if not df.empty:
            dfs[pais] = df.set_index("year")["value"]

# Mostrar gráfica
if dfs:
    combined = pd.DataFrame(dfs)
    st.subheader(f"{indicador}")
    st.line_chart(combined)
    st.dataframe(combined, use_container_width=True)
else:
    st.warning("No se encontraron datos.")