from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import numpy as np
import joblib
import os
import httpx
from sklearn.ensemble import IsolationForest


# 1. PATHS

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "backend", "models")
DATA_PATH = os.path.join(BASE_DIR, "dataset", "hourly_processed.csv")


# 2. LOAD MODEL

rf_bundle = joblib.load(os.path.join(MODEL_DIR, "rf_model.pkl"))
rf_model  = rf_bundle["model"]
FEATURES  = rf_bundle["features"]


# 3. LOAD DATA

df = pd.read_csv(DATA_PATH, index_col="datetime", parse_dates=True)


# 4. ANOMALY DETECTOR

iso_forest = IsolationForest(contamination=0.05, random_state=42)
iso_forest.fit(df[["Global_active_power"]].dropna())
print("Anomaly detector ready")


# 5. INDIA STATE ELECTRICITY RATES
# Domestic slab rates (₹/unit) for all Indian states
# Format: list of (upto_units, rate_per_unit)

STATE_RATES = {
    "Andhra Pradesh": {
        "board": "APSPDCL / APEPDCL",
        "slabs": [(50, 1.45), (100, 2.60), (200, 3.50), (300, 5.00), (float("inf"), 7.50)]
    },
    "Telangana": {
        "board": "TSSPDCL / TSNPDCL",
        "slabs": [(50, 1.45), (100, 2.60), (200, 3.50), (300, 4.50), (float("inf"), 7.00)]
    },
    "Karnataka": {
        "board": "BESCOM / HESCOM",
        "slabs": [(30, 3.15), (100, 5.55), (200, 7.10), (float("inf"), 8.35)]
    },
    "Tamil Nadu": {
        "board": "TANGEDCO",
        "slabs": [(100, 0.00), (200, 1.50), (500, 3.50), (float("inf"), 5.50)]
    },
    "Kerala": {
        "board": "KSEB",
        "slabs": [(40, 2.90), (80, 3.50), (140, 4.70), (180, 5.50), (float("inf"), 6.90)]
    },
    "Maharashtra": {
        "board": "MSEDCL",
        "slabs": [(100, 3.46), (300, 7.61), (500, 10.38), (float("inf"), 11.47)]
    },
    "Gujarat": {
        "board": "DGVCL / MGVCL / PGVCL / UGVCL",
        "slabs": [(50, 2.35), (200, 3.60), (float("inf"), 5.00)]
    },
    "Rajasthan": {
        "board": "JVVNL / AVVNL / JDVVNL",
        "slabs": [(50, 3.00), (150, 4.75), (300, 6.00), (float("inf"), 6.75)]
    },
    "Madhya Pradesh": {
        "board": "MPPKVVCL / MPMKVVCL",
        "slabs": [(50, 3.47), (150, 4.67), (300, 5.87), (float("inf"), 6.37)]
    },
    "Uttar Pradesh": {
        "board": "UPPCL",
        "slabs": [(100, 3.35), (150, 3.85), (300, 5.00), (float("inf"), 6.00)]
    },
    "Delhi": {
        "board": "BSES / Tata Power",
        "slabs": [(200, 3.00), (400, 4.50), (float("inf"), 6.50)]
    },
    "Haryana": {
        "board": "DHBVN / UHBVN",
        "slabs": [(50, 2.00), (100, 2.50), (200, 5.25), (400, 6.30), (float("inf"), 7.10)]
    },
    "Punjab": {
        "board": "PSPCL",
        "slabs": [(100, 4.19), (300, 5.46), (500, 6.69), (float("inf"), 7.10)]
    },
    "Himachal Pradesh": {
        "board": "HPSEBL",
        "slabs": [(60, 0.55), (125, 1.60), (200, 3.30), (float("inf"), 4.65)]
    },
    "Uttarakhand": {
        "board": "UPCL",
        "slabs": [(100, 3.10), (200, 4.50), (400, 5.85), (float("inf"), 6.30)]
    },
    "Bihar": {
        "board": "NBPDCL / SBPDCL",
        "slabs": [(100, 4.69), (200, 5.59), (400, 6.19), (float("inf"), 6.69)]
    },
    "Jharkhand": {
        "board": "JBVNL",
        "slabs": [(100, 3.25), (200, 4.50), (400, 5.25), (float("inf"), 5.75)]
    },
    "West Bengal": {
        "board": "WBSEDCL / CESC",
        "slabs": [(75, 4.33), (150, 5.48), (250, 6.21), (float("inf"), 7.02)]
    },
    "Odisha": {
        "board": "TPCODL / NESCO / WESCO / SOUTHCO",
        "slabs": [(50, 1.90), (200, 3.60), (400, 4.80), (float("inf"), 5.50)]
    },
    "Chhattisgarh": {
        "board": "CSPDCL",
        "slabs": [(30, 2.50), (60, 3.50), (100, 4.50), (200, 5.00), (float("inf"), 5.50)]
    },
    "Assam": {
        "board": "APDCL",
        "slabs": [(50, 3.50), (120, 5.00), (250, 6.00), (float("inf"), 6.80)]
    },
    "Goa": {
        "board": "GPDCL",
        "slabs": [(100, 1.70), (200, 3.20), (float("inf"), 4.50)]
    },
    "Jammu & Kashmir": {
        "board": "JKPDCL",
        "slabs": [(100, 1.68), (200, 2.27), (400, 2.84), (float("inf"), 3.39)]
    },
    "Meghalaya": {
        "board": "MePDCL",
        "slabs": [(100, 4.30), (200, 5.80), (float("inf"), 7.00)]
    },
    "Tripura": {
        "board": "TSECL",
        "slabs": [(50, 2.50), (150, 4.00), (float("inf"), 5.50)]
    },
}


def calculate_bill(units: float, state: str) -> dict:
    state_data = STATE_RATES.get(state, STATE_RATES["Telangana"])
    slabs      = state_data["slabs"]
    bill       = 0.0
    prev       = 0
    detail     = []
    remaining  = units

    for limit, rate in slabs:
        if remaining <= 0:
            break
        slab_units = min(remaining, limit - prev)
        slab_cost  = slab_units * rate
        detail.append({
            "slab":  f"{prev}–{int(limit) if limit != float('inf') else str(prev) + '+'}",
            "units": round(slab_units, 2),
            "rate":  rate,
            "cost":  round(slab_cost, 2),
        })
        bill      += slab_cost
        remaining -= slab_units
        prev       = limit

    return {
        "total_bill": round(bill, 2),
        "slabs":      detail,
        "board":      state_data["board"],
        "state":      state,
    }


# 6. HELPER

def clean(records: list) -> list:
    cleaned = []
    for row in records:
        cleaned.append({
            k: (None if (isinstance(v, float) and (np.isnan(v) or np.isinf(v))) else v)
            for k, v in row.items()
        })
    return cleaned


# 7. APP

app = FastAPI(title="EnergyInsight API", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# 8. SCHEMAS

class PredictRequest(BaseModel):
    hour: int
    day_of_week: int
    month: int
    is_weekend: int
    rolling_mean_1h: float
    rolling_mean_24h: float
    lag_1h: float
    lag_24h: float
    Voltage: float
    Global_intensity: float
    Sub_metering_1: float
    Sub_metering_2: float
    Sub_metering_3: float
    state: Optional[str] = "Telangana"

class CostRequest(BaseModel):
    predicted_kw: float
    hours_per_day: float = 24.0
    days: int = 30
    state: str = "Telangana"


# 9. ROUTES

@app.get("/")
def root():
    return {"message": "EnergyInsight API v3.0 — All India rates"}


@app.get("/states")
def get_states():
    return {
        "states": [
            {"name": s, "board": v["board"]}
            for s, v in sorted(STATE_RATES.items())
        ]
    }


@app.post("/predict")
def predict(data: PredictRequest):
    input_df   = pd.DataFrame([data.dict()])[FEATURES]
    prediction = rf_model.predict(input_df)[0]
    pred_kw    = round(float(prediction), 4)

    units_per_month = pred_kw * 24 * 30
    bill = calculate_bill(units_per_month, data.state)

    return {
        "predicted_power_kw":    pred_kw,
        "unit":                  "kW",
        "model":                 "Random Forest",
        "state":                 data.state,
        "estimated_monthly_kwh": round(units_per_month, 2),
        "estimated_bill":        bill,
    }


@app.post("/cost")
def cost_calculator(data: CostRequest):
    units = data.predicted_kw * data.hours_per_day * data.days
    bill  = calculate_bill(units, data.state)
    return {
        "input_kw":      data.predicted_kw,
        "hours_per_day": data.hours_per_day,
        "days":          data.days,
        "total_units":   round(units, 2),
        "bill":          bill,
    }


@app.get("/stats/summary")
def summary_stats():
    stats = df["Global_active_power"].describe().round(4).to_dict()
    return {
        "date_range":          {"start": str(df.index.min()), "end": str(df.index.max())},
        "total_records":       len(df),
        "global_active_power": stats,
    }

@app.get("/stats/hourly")
def hourly_avg():
    avg = (
        df.groupby("hour")["Global_active_power"]
        .mean().round(4).reset_index()
        .rename(columns={"Global_active_power": "avg_power_kw"})
    )
    return clean(avg.to_dict(orient="records"))

@app.get("/stats/daily")
def daily_avg():
    daily = (
        df["Global_active_power"].resample("D").mean()
        .round(4).dropna().reset_index()
        .rename(columns={"datetime": "date", "Global_active_power": "avg_power_kw"})
    )
    daily["date"] = daily["date"].astype(str)
    return clean(daily.tail(365).to_dict(orient="records"))

@app.get("/stats/weekday-vs-weekend")
def weekday_vs_weekend():
    weekday = df[df["is_weekend"] == 0].groupby("hour")["Global_active_power"].mean().round(4)
    weekend = df[df["is_weekend"] == 1].groupby("hour")["Global_active_power"].mean().round(4)
    return [
        {"hour": h, "weekday_kw": round(float(weekday.get(h, 0)), 4),
         "weekend_kw": round(float(weekend.get(h, 0)), 4)}
        for h in range(24)
    ]

@app.get("/stats/monthly")
def monthly_avg():
    monthly = (
        df.groupby("month")["Global_active_power"]
        .mean().round(4).reset_index()
        .rename(columns={"Global_active_power": "avg_power_kw"})
    )
    names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
             7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    monthly["month_name"] = monthly["month"].map(names)
    return clean(monthly.to_dict(orient="records"))

@app.get("/stats/anomalies")
def get_anomalies():
    daily = (
        df["Global_active_power"].resample("D").mean()
        .dropna().reset_index()
        .rename(columns={"datetime": "date", "Global_active_power": "avg_power_kw"})
    )
    preds = iso_forest.predict(daily[["avg_power_kw"]].values)
    daily["is_anomaly"]   = (preds == -1).astype(int)
    daily["date"]         = daily["date"].astype(str)
    daily["avg_power_kw"] = daily["avg_power_kw"].round(4)
    return clean(daily.tail(365).to_dict(orient="records"))

@app.get("/realtime/weather")
async def get_weather():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=17.385&longitude=78.4867"
        "&current=temperature_2m,relative_humidity_2m,"
        "apparent_temperature,weather_code,wind_speed_10m,cloud_cover"
        "&timezone=Asia%2FKolkata"
    )
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(url)
            data = resp.json()
        current     = data["current"]
        temp        = current["temperature_2m"]
        base_mean   = float(df["Global_active_power"].mean())
        heat_factor = max(0, (temp - 25) * 0.03)
        return {
            "location":          "Hyderabad, Telangana",
            "temperature_c":     temp,
            "apparent_temp_c":   current["apparent_temperature"],
            "humidity_pct":      current["relative_humidity_2m"],
            "wind_speed_kmh":    current["wind_speed_10m"],
            "cloud_cover_pct":   current["cloud_cover"],
            "weather_code":      current["weather_code"],
            "estimated_load_kw": round(base_mean * (1 + heat_factor), 4),
            "heat_factor_pct":   round(heat_factor * 100, 1),
        }
    except Exception as e:
        return {"error": str(e), "message": "Weather API unavailable"}

@app.get("/plots")
def list_plots():
    plots_dir = os.path.join(BASE_DIR, "backend", "plots")
    files     = [f for f in os.listdir(plots_dir) if f.endswith(".png")]
    return {"plots": files}