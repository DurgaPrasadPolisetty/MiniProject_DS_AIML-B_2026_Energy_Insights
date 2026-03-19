# ⚡ EnergyInsight

**Predicting Household Energy Consumption Using Data Analytics**

A full-stack machine learning web application that analyzes electricity usage patterns and predicts future energy demand using the UCI Household Power Consumption dataset.

---

## 🚀 Features

- **ML Models** — Linear Regression, Random Forest, LSTM trained and compared
- **Best Model** — Random Forest (R² ≈ 1.00, RMSE ≈ 0.04)
- **Real-time Weather** — Live Hyderabad weather via Open-Meteo API with load estimation
- **Anomaly Detection** — Isolation Forest flags unusual consumption days
- **Bill Estimator** — All 25 Indian states with actual electricity board slab rates
- **Interactive Dashboard** — 4 live charts with daily, hourly, weekly, monthly patterns
- **FastAPI Backend** — 8 REST endpoints
- **React Frontend** — Green energy themed responsive UI

---

## 🗂️ Project Structure

```
Energy_insights/
├── backend/
│   ├── app.py                  # FastAPI application
│   ├── data_preprocessing.py   # Data cleaning + feature engineering
│   ├── model.py                # Model training + evaluation
│   └── models/                 # Saved model files (generate locally)
├── dataset/
│   └── hourly_processed.csv    # Preprocessed hourly data
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── components/
│   │       ├── Dashboard.jsx
│   │       └── Predict.jsx
│   └── package.json
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/EnergyInsight.git
cd EnergyInsight
```

### 2. Backend setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Download dataset

Download the UCI Household Power Consumption dataset from:
https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption

Place `household_power_consumption.txt` inside the `dataset/` folder.

### 4. Run preprocessing

```bash
python data_preprocessing.py
```

### 5. Train models (or use Google Colab)

```bash
python model.py
```

This saves `rf_model.pkl` to `backend/models/`.

### 6. Start FastAPI backend

```bash
uvicorn app:app --reload
```

API runs at `http://127.0.0.1:8000`
Swagger docs at `http://127.0.0.1:8000/docs`

### 7. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:5173`

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/states` | All Indian states + board names |
| POST | `/predict` | Predict power + bill for selected state |
| POST | `/cost` | Bill calculator |
| GET | `/stats/summary` | Dataset summary stats |
| GET | `/stats/hourly` | Avg power by hour of day |
| GET | `/stats/daily` | Daily avg power (last 365 days) |
| GET | `/stats/weekday-vs-weekend` | Hourly weekday vs weekend comparison |
| GET | `/stats/monthly` | Monthly average power |
| GET | `/stats/anomalies` | Anomaly detection results |
| GET | `/realtime/weather` | Live weather + estimated load |

---

## 🤖 Models Trained

| Model | RMSE | MAE | R² |
|-------|------|-----|----|
| Linear Regression | ~0.04 | ~0.02 | ~1.00 |
| **Random Forest** | **~0.04** | **~0.02** | **~1.00** |
| LSTM | ~0.46 | ~0.31 | ~0.62 |

**Random Forest** selected as best model for production.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Data processing | Python, Pandas, NumPy |
| Machine learning | Scikit-learn, TensorFlow/Keras |
| Backend API | FastAPI, Uvicorn |
| Frontend | React, Recharts, Axios |
| Styling | CSS Variables, Green Energy Theme |
| Real-time data | Open-Meteo API |

---

## 📊 Dataset

**UCI Individual Household Electric Power Consumption**
- Source: https://archive.ics.uci.edu/dataset/235
- Raw size: 2,049,280 rows × 7 columns (minute-level)
- After preprocessing: 34,144 hourly records × 16 features
- Date range: December 2006 — November 2010