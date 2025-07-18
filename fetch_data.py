# fetch_daily.py

import requests
import pandas as pd
from datetime import datetime
import os

# --- Config ---
LAT = 44.34
LON = 10.99
API_KEY = '85e0f0f1a60b006725a72b69e53d16c2'  # GitHub Actions will set this as a secret

# --- API Call ---
url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&units=metric&appid={API_KEY}"
response = requests.get(url)
data = response.json()

# --- Extract wind speed and direction ---
wind_speed = data['wind']['speed']
wind_deg = data['wind']['deg']
now_utc = datetime.utcnow()

# --- Prepare a DataFrame entry ---
record = {
    'datetime': now_utc,
    'wind_speed': wind_speed,
    'wind_deg': wind_deg
}
df = pd.DataFrame([record])

# --- CSV path ---
csv_path = "data/wind_data.csv"
os.makedirs("data", exist_ok=True)

# --- Save or update ---
if os.path.exists(csv_path):
    old_df = pd.read_csv(csv_path, parse_dates=['datetime'])
    combined = pd.concat([old_df, df], ignore_index=True).drop_duplicates(subset='datetime')
else:
    combined = df

combined.to_csv(csv_path, index=False)
print(f"✅ Logged data at {now_utc}.")
