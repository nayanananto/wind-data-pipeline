# fetch_daily.py

import requests
import pandas as pd
from datetime import datetime, timezone
import os
import math

# --- Config ---
LAT = 44.34
LON = 10.99
API_KEY = os.environ.get("API_KEY")  # GitHub Actions will set this as a secret

if not API_KEY:
    raise ValueError("API_KEY is not set. Add it as a GitHub Actions secret.")

# --- API Call (OpenWeatherMap Current Weather) ---
url = "https://api.openweathermap.org/data/2.5/weather"
params = {
    "lat": LAT,
    "lon": LON,
    "units": "metric",
    "appid": API_KEY
}
response = requests.get(url, params=params, timeout=30)
response.raise_for_status()
data = response.json()

# --- Extract required fields safely ---
now_utc = datetime.now(timezone.utc)

wind_speed_10m = data.get("wind", {}).get("speed")
wind_direction_10m = data.get("wind", {}).get("deg")
wind_gusts_10m = data.get("wind", {}).get("gust")  # may be missing

temperature_2m = data.get("main", {}).get("temp")
relative_humidity_2m = data.get("main", {}).get("humidity")

dir_rad = float(wind_direction_10m) * math.pi / 180.0
wind_dir_sin = math.sin(dir_rad)
wind_dir_cos = math.cos(dir_rad)

# --- Prepare a DataFrame entry with your target column names ---
record = {
    "datetime": now_utc.isoformat(),
    "wind_speed": wind_speed_10m,
    "wind_dir_sin": wind_dir_sin,
    "wind_dir_cos": wind_dir_cos,
    "wind_gusts_10m_ms": wind_gusts_10m,
    "temperature_2m_c": temperature_2m,
    "relative_humidity_2m": relative_humidity_2m,
}
df = pd.DataFrame([record])

# --- CSV path ---
csv_path = "data/wind_data.csv"
os.makedirs("data", exist_ok=True)

# --- Save or update ---
if os.path.exists(csv_path):
    old_df = pd.read_csv(csv_path)

    # normalize datetime for dedupe
    old_df["datetime"] = pd.to_datetime(old_df["datetime"], utc=True, errors="coerce")
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True, errors="coerce")

    combined = (
        pd.concat([old_df, df], ignore_index=True)
        .drop_duplicates(subset="datetime")
        .sort_values("datetime")
    )
else:
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True, errors="coerce")
    combined = df.sort_values("datetime")

combined.to_csv(csv_path, index=False)
print(f"✅ Logged data at {now_utc.isoformat()}.")
