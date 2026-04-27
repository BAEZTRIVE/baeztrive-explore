import requests
import pandas as pd

# Mapa de indicadores del Banco Mundial
WB_INDICATORS = {
    "PIB (USD)": "NY.GDP.MKTP.CD",
    "PIB per cápita (USD)": "NY.GDP.PCAP.CD",
    "Población": "SP.POP.TOTL",
    "Gini": "SI.POV.GINI",
    "Pobreza extrema (%)": "SI.POV.DDAY",
}

def fetch_world_bank(indicator_code, country_code, start_year=2000, end_year=2023):
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}"
    params = {
        "date": f"{start_year}:{end_year}",
        "format": "json",
        "per_page": 100
    }

    for intento in range(3):  # 3 intentos
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            records = data[1]

            df = pd.DataFrame([{
                "year": int(r["date"]),
                "value": r["value"],
                "country": r["country"]["value"]
            } for r in records if r["value"] is not None])

            return df.sort_values("year")

        except Exception as e:
            print(f"  Intento {intento + 1} fallido: {e}")

    print(f"  ⚠️ No se pudo obtener {indicator_code} para {country_code}")
    return pd.DataFrame()


def fetch_all_wb_indicators(country_code="MX"):
    """Jala todos los indicadores del Banco Mundial para un país."""
    result = {}
    for name, code in WB_INDICATORS.items():
        print(f"Jalando: {name}...")
        result[name] = fetch_world_bank(code, country_code)
    return result


# Test
if __name__ == "__main__":
    data = fetch_all_wb_indicators("MX")
    for name, df in data.items():
        print(f"\n--- {name} ---")
        print(df.tail(3))