import requests
import pandas as pd
import io

def fetch_hdi(country_code="MEX", start_year=2000, end_year=2022):
    """
    Jala el IDH del Human Development Report del PNUD.
    Usa código ISO3 (MEX, BRA, ARG)
    """
    url = "https://hdr.undp.org/sites/default/files/2023-24_HDR/HDR23-24_Composite_indices_complete_time_series.csv"
    
    print("Jalando IDH del PNUD...")
    response = requests.get(url, timeout=30)
    
    df_raw = pd.read_csv(io.StringIO(response.text), encoding="latin-1")
    
    # Filtrar por país
    df_country = df_raw[df_raw["iso3"] == country_code].copy()
    
    # Las columnas de IDH vienen como hdi_2000, hdi_2001, etc.
    hdi_cols = [col for col in df_country.columns if col.startswith("hdi_") and col[4:].isdigit()]
    
    records = []
    for col in hdi_cols:
        year = int(col[4:])
        if start_year <= year <= end_year:
            value = df_country[col].values[0]
            if pd.notna(value):
                records.append({"year": year, "value": float(value), "country": country_code})
    
    df = pd.DataFrame(records).sort_values("year")
    return df


# Test
if __name__ == "__main__":
    df = fetch_hdi("MEX")
    print(df)