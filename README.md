# EnergyInsight: Predicting Household Energy Consumption Using Data Analytics

---

## Abstract

EnergyInsight is a full-stack data analytics and machine learning web application designed to analyze, predict, and visualize household electricity consumption patterns. The project leverages over 2 million real-world minute-level electricity readings collected from a single household in France over a period of four years (2006–2010). After thorough data preprocessing and feature engineering, the dataset was resampled to 34,144 hourly records with 16 meaningful features. Three machine learning models — Linear Regression, Random Forest, and LSTM — were trained and evaluated using standard regression metrics. Random Forest emerged as the best-performing model with an R² score of approximately 1.00 and an RMSE of 0.04 kW. The application provides an interactive React-based dashboard with real-time weather integration using GPS-based location detection, anomaly detection powered by Isolation Forest, a 7-day consumption forecast, and a common-user-friendly electricity bill estimator supporting all 25 Indian states with their official electricity board slab rates. The project bridges data science and practical energy management for everyday households.

---

## Problem Statement

Efficient energy consumption is essential for sustainable living and cost management. Most households in India have no visibility into their electricity usage patterns — they only see the final bill at the end of the month without understanding which appliances, hours, or seasons are driving their consumption. This lack of insight leads to unnecessary energy waste, unexpectedly high bills, and an increased carbon footprint. This project addresses this problem by analyzing historical electricity usage data to discover patterns, detect anomalies, predict future demand, and estimate electricity bills using state-specific Indian electricity board slab rates — making energy data accessible and actionable for common users.

---

## Dataset Source

| Property       | Details                                                                 |
|----------------|-------------------------------------------------------------------------|
| Name           | Individual Household Electric Power Consumption                         |
| Source         | UCI Machine Learning Repository                                         |
| URL            | https://archive.ics.uci.edu/dataset/235                                 |
| Size           | 2,049,280 rows × 7 columns (minute-level readings)                     |
| Duration       | December 2006 — November 2010 (4 years)                                |
| Location       | Sceaux, France (suburb of Paris)                                        |

### Dataset Columns

| Column                  | Description                                      |
|-------------------------|--------------------------------------------------|
| Date                    | Date of measurement (DD/MM/YYYY)                |
| Time                    | Time of measurement (HH:MM:SS)                  |
| Global_active_power     | Total active power consumed (kW) — Target       |
| Global_reactive_power   | Reactive power consumed (kW)                    |
| Voltage                 | Household voltage (V)                           |
| Global_intensity        | Current intensity (A)                           |
| Sub_metering_1          | Kitchen appliances energy (Wh)                  |
| Sub_metering_2          | Laundry room energy (Wh)                        |
| Sub_metering_3          | AC, water heater, electric heater energy (Wh)   |

---

## Methodology / Workflow

```
Raw Dataset (2M rows)
        ↓
  Data Preprocessing
  • Parse datetime from Date + Time columns
  • Handle missing values ('?' → NaN) via interpolation
  • Convert all columns to numeric types
  • Drop rows with missing target (Global_active_power)
        ↓
  Feature Engineering
  • Time features: hour, day_of_week, month, is_weekend
  • Lag features: lag_1h, lag_24h
  • Rolling averages: rolling_mean_1h, rolling_mean_24h
  • Energy conversion: energy_kwh = Global_active_power / 60
        ↓
  Resampling
  • Aggregate minute-level → hourly (mean/sum)
  • Final: 34,144 rows × 16 features
        ↓
  Model Training (Google Colab — GPU)
  • Linear Regression (baseline)
  • Random Forest Regressor (100 trees, max_depth=15)
  • LSTM (2 layers, 64+32 units, EarlyStopping)
  • Train/Test split: 80% / 20% (time-ordered, no shuffle)
        ↓
  Model Evaluation
  • Metrics: RMSE, MAE, R² Score
  • Best model selected: Random Forest
  • Model saved as rf_model.pkl
        ↓
  Backend API (FastAPI)
  • /simple-predict → bill + tips + forecast for users
  • /stats/* → hourly, daily, monthly, anomaly endpoints
  • /realtime/weather → GPS-based live weather via Open-Meteo
  • /states → 25 Indian state electricity board rates
        ↓
  Frontend Dashboard (React)
  • Live weather card with GPS location detection
  • 5 interactive charts (daily, hourly, weekly, monthly, submetering)
  • Anomaly detection markers on daily chart
  • 7-day forecast extension
  • Bill estimator with TSSPDCL / all-India slab rates
  • Savings calculator and personalised energy tips
```

---

## Tools Used

| Category              | Tools / Libraries                                      |
|-----------------------|--------------------------------------------------------|
| Programming Language  | Python 3.11, JavaScript (ES2022)                       |
| Data Processing       | Pandas, NumPy                                          |
| Machine Learning      | Scikit-learn (Random Forest, Linear Regression, Isolation Forest) |
| Deep Learning         | TensorFlow 2.x / Keras (LSTM)                         |
| Model Persistence     | Joblib                                                 |
| Data Visualization    | Matplotlib, Seaborn (plots), Recharts (dashboard)      |
| Backend Framework     | FastAPI, Uvicorn                                       |
| Frontend Framework    | React 18, Vite                                         |
| HTTP Client           | Axios (frontend), HTTPX (backend)                      |
| Real-time Weather     | Open-Meteo API (free, no key required)                 |
| Reverse Geocoding     | Nominatim / OpenStreetMap                              |
| Development Tools     | VS Code, Google Colab, Git, GitHub                     |
| Environment           | Python venv, Node.js 18+                               |

---

## Results / Findings

### Model Performance

| Model              | RMSE   | MAE    | R² Score | Selected |
|--------------------|--------|--------|----------|----------|
| Linear Regression  | ~0.04  | ~0.02  | ~1.00    |          |
| **Random Forest**  | **~0.04** | **~0.02** | **~1.00** | ✅ Yes |
| LSTM               | ~0.46  | ~0.31  | ~0.62    |          |

### Key Findings from Data Analysis

- **Peak consumption hours** occur between 7 PM and 10 PM daily — the evening peak accounts for nearly 2x the off-peak consumption
- **Winter months** (January, February) show 25–30% higher electricity consumption compared to summer months (July, August)
- **Weekends** show different consumption patterns — higher afternoon usage and lower morning usage compared to weekdays
- **Anomaly detection** using Isolation Forest successfully identified 5% of days with unusual consumption patterns
- **Sub-metering analysis** revealed that AC and water heating (Sub_metering_3) account for the largest share of energy use among measured appliances
- **Random Forest outperformed LSTM** because engineered lag and rolling features already provided sufficient temporal context, negating LSTM's sequence-learning advantage on this tabular dataset
- A **10% reduction** in consumption translates to approximately ₹150–500/month in savings depending on the state and slab

### Application Features Delivered

- Real-time GPS weather integration with load estimation based on temperature
- All 25 Indian state electricity board slab rates for accurate bill calculation
- 3-month seasonal bill forecast using historical consumption patterns
- Personalised energy-saving tips based on consumption level
- Carbon footprint calculator (CO₂ kg and tree equivalent)
- Savings calculator with interactive slider

---

## Team Members

| Name                  | Role                          | Responsibilities                                      |
|-----------------------|-------------------------------|-------------------------------------------------------|
| Durga Prasad Polisetty | Full Stack Developer & ML Engineer | Data preprocessing, model training, FastAPI backend, React frontend, deployment |

---

## How to Run

### Backend

```bash
git clone https://github.com/DurgaPrasadPolisetty/EnergyInsights.git
cd EnergyInsights
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cd backend
uvicorn app:app --reload
# API runs at http://127.0.0.1:8000
# Docs at http://127.0.0.1:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# App runs at http://localhost:5173
```

---

## GitHub Repository

🔗 [https://github.com/DurgaPrasadPolisetty/EnergyInsights](https://github.com/DurgaPrasadPolisetty/EnergyInsights)
