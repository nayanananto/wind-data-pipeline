import requests
import pandas as pd
from datetime import datetime
import os

# Load your API key from GitHub secrets or a local .env file
API_KEY = 'ce14efec496ea4748b79ac46d82fecbb'
LAT, LON = 51.5074, -0.1278  # Example: London
url = f"https://api.openweathermap.org/data/2.5/onecall?lat={LAT}&lon={LON}&exclude=current,minutely,daily,alerts&units=metric&appid={API_KEY}"

response = requests.get(url)
data = response.json()
hourly_data = data.get('hourly', [])

rows = []
for hour in hourly_data:
    dt = datetime.utcfromtimestamp(hour['dt'])
    wind_speed = hour.get('wind_speed')
    wind_deg = hour.get('wind_deg')  # Wind direction in degrees (0–360)
    if wind_speed is not None and wind_deg is not None:
        rows.append({
            'datetime': dt,
            'wind_speed': wind_speed,
            'wind_deg': wind_deg
        })

# Load existing data if exists
csv_path = 'data/wind_data.csv'
if os.path.exists(csv_path):
    existing_df = pd.read_csv(csv_path, parse_dates=['datetime'])
    df = pd.DataFrame(rows)
    combined = pd.concat([existing_df, df]).drop_duplicates(subset='datetime').sort_values('datetime')
else:
    combined = pd.DataFrame(rows)

# Save updated data
combined.to_csv(csv_path, index=False)
print("✅ Wind speed and direction updated.")
