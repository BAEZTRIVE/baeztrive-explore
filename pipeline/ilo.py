import requests
import pandas as pd

def fetch_informality(country_code="MEX", start_year=2000, end_year=2023):
    """
    Jala el porcentaje de empleo informal de ILOSTAT (OIT).
    Indicador SDG 8.3.1 - Proporción de empleo informal (%)
    """
    url = "https://rplumber.ilo.org/data/indicator/"
    params = {
        "id": "SDG_0831_SEX_ECO_RT_A",
        "ref_area": country_code,
        "sex": "SEX_T",
        "classif1": "ECO_AGGREGATE_TOTAL",
        "timefrom": start_year,
        "timeto": end_year,
        "type": "label",
        "format": "JSON"
    }

    print("Jalando informalidad de ILOSTAT...")
    response = requests.get(url, params=params, timeout=30)
    data = response.json()

    records = []
    for item in data:
        records.append({
            "year": int(item["time"]),
            "value": float(item["obs_value"]),
            "country": item["ref_area.label"]
        })

    df = pd.DataFrame(records).sort_values("year")
    return df


# Test
if __name__ == "__main__":
    df = fetch_informality("MEX")
    print(df)