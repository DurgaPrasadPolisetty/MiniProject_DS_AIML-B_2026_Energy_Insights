import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os


# 1. LOAD DATASET

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "dataset", "household_power_consumption.txt")

def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(
        path,
        sep=";",
        low_memory=False,
        na_values=["?"],
    )
    df["datetime"] = pd.to_datetime(
        df["Date"] + " " + df["Time"],
        dayfirst=True
    )
    df.drop(columns=["Date", "Time"], inplace=True)
    df.set_index("datetime", inplace=True)
    return df


# 2. CLEAN DATA

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df.dropna(subset=["Global_active_power"], inplace=True)
    df.interpolate(method="time", inplace=True)
    df.dropna(inplace=True)

    print(f"Clean dataset shape: {df.shape}")
    return df


# 3. FEATURE ENGINEERING

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["hour"]        = df.index.hour
    df["day_of_week"] = df.index.dayofweek
    df["month"]       = df.index.month
    df["is_weekend"]  = (df.index.dayofweek >= 5).astype(int)

    df["rolling_mean_1h"]  = df["Global_active_power"].rolling(window=60,   min_periods=1).mean()
    df["rolling_mean_24h"] = df["Global_active_power"].rolling(window=1440, min_periods=1).mean()

    df["lag_1h"]  = df["Global_active_power"].shift(60)
    df["lag_24h"] = df["Global_active_power"].shift(1440)

    df["energy_kwh"] = df["Global_active_power"] / 60.0

    df.dropna(inplace=True)
    print(f"Features added. Final shape: {df.shape}")
    return df


# 4. RESAMPLE TO HOURLY

def resample_hourly(df: pd.DataFrame) -> pd.DataFrame:
    hourly = df.resample("h").agg({
        "Global_active_power":   "mean",
        "Global_reactive_power": "mean",
        "Voltage":               "mean",
        "Global_intensity":      "mean",
        "Sub_metering_1":        "sum",
        "Sub_metering_2":        "sum",
        "Sub_metering_3":        "sum",
        "energy_kwh":            "sum",
        "hour":                  "first",
        "day_of_week":           "first",
        "month":                 "first",
        "is_weekend":            "first",
        "rolling_mean_1h":       "mean",
        "rolling_mean_24h":      "mean",
        "lag_1h":                "mean",
        "lag_24h":               "mean",
    })
    hourly.dropna(inplace=True)
    print(f"Hourly resampled shape: {hourly.shape}")
    return hourly


# 5. SUMMARY STATS

def print_summary(df: pd.DataFrame):
    print("\n Dataset Summary")
    print(f"  Date range : {df.index.min()} to {df.index.max()}")
    print(f"  Records    : {len(df):,}")
    print(f"  Columns    : {list(df.columns)}")
    print("\n Global Active Power stats")
    print(df["Global_active_power"].describe().round(4))


# 6. VISUALISATIONS

PLOTS_DIR = os.path.join(BASE_DIR, "backend", "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

def plot_daily_consumption(hourly: pd.DataFrame):
    daily = hourly["Global_active_power"].resample("D").mean()
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.plot(daily.index, daily.values, linewidth=0.8, color="#4C6EF5")
    ax.fill_between(daily.index, daily.values, alpha=0.15, color="#4C6EF5")
    ax.set_title("Average Daily Global Active Power (kW)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Power (kW)")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "daily_consumption.png"), dpi=120)
    plt.close()
    print("Saved: daily_consumption.png")

def plot_hourly_heatmap(hourly: pd.DataFrame):
    pivot = hourly.copy()
    pivot["date"] = pivot.index.date
    pivot["hour"] = pivot.index.hour
    hmap = pivot.pivot_table(
        index="date", columns="hour",
        values="Global_active_power", aggfunc="mean"
    ).tail(90)
    fig, ax = plt.subplots(figsize=(14, 6))
    sns.heatmap(hmap.T, cmap="YlOrRd", ax=ax,
                cbar_kws={"label": "Avg Power (kW)"}, linewidths=0)
    ax.set_title("Hourly Power Heatmap - Last 90 Days")
    ax.set_xlabel("Date")
    ax.set_ylabel("Hour of Day")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "hourly_heatmap.png"), dpi=120)
    plt.close()
    print("Saved: hourly_heatmap.png")

def plot_avg_by_hour(hourly: pd.DataFrame):
    avg = hourly.groupby("hour")["Global_active_power"].mean()
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(avg.index, avg.values, color="#4C6EF5", edgecolor="none")
    ax.set_title("Average Power Consumption by Hour of Day")
    ax.set_xlabel("Hour")
    ax.set_ylabel("Avg Power (kW)")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "avg_by_hour.png"), dpi=120)
    plt.close()
    print("Saved: avg_by_hour.png")

def plot_weekday_vs_weekend(hourly: pd.DataFrame):
    wday = hourly[hourly["is_weekend"] == 0].groupby("hour")["Global_active_power"].mean()
    wend = hourly[hourly["is_weekend"] == 1].groupby("hour")["Global_active_power"].mean()
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(wday.index, wday.values, label="Weekday", color="#4C6EF5")
    ax.plot(wend.index, wend.values, label="Weekend", color="#F76707")
    ax.set_title("Weekday vs Weekend - Avg Power by Hour")
    ax.set_xlabel("Hour")
    ax.set_ylabel("Avg Power (kW)")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "weekday_vs_weekend.png"), dpi=120)
    plt.close()
    print("Saved: weekday_vs_weekend.png")


# 7. SAVE PROCESSED DATA

PROCESSED_PATH = os.path.join(BASE_DIR, "dataset", "hourly_processed.csv")

def save_processed(hourly: pd.DataFrame):
    hourly.to_csv(PROCESSED_PATH)
    print(f"Processed dataset saved to {PROCESSED_PATH}")


# 8. MAIN PIPELINE

def run_pipeline() -> pd.DataFrame:
    print("Loading raw data ...")
    df = load_data()

    print("Cleaning ...")
    df = clean_data(df)

    print("Engineering features ...")
    df = add_features(df)

    print("Resampling to hourly ...")
    hourly = resample_hourly(df)

    print_summary(hourly)

    print("\nGenerating plots ...")
    plot_daily_consumption(hourly)
    plot_hourly_heatmap(hourly)
    plot_avg_by_hour(hourly)
    plot_weekday_vs_weekend(hourly)

    save_processed(hourly)
    return hourly


if __name__ == "__main__":
    run_pipeline()