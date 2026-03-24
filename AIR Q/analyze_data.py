
import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv('e:\\Air Quality\\global_air_quality_dataset.csv')

# Statistics for relevant columns
cols = ['Temperature (AC)', 'Humidity (%)', 'CO (ppm)', 'AQI']
# Note: The column names in the previous cat output had encoding artifacts "AC".
# I'll try to match them or just print all columns to be sure.

print("Columns:", df.columns.tolist())

# Rename for easier access if needed, but printing stats first
for col in df.columns:
    if 'Temperature' in col:
        print(f"\nStats for {col}:")
        print(df[col].describe())
    if 'Humidity' in col:
        print(f"\nStats for {col}:")
        print(df[col].describe())
    if 'CO' in col:
        print(f"\nStats for {col}:")
        print(df[col].describe())
    if 'AQI' in col:
        print(f"\nStats for {col}:")
        print(df[col].describe())

# Check AQI categories if we were to define them
def get_aqi_category(aqi):
    if aqi <= 50: return "Good"
    elif aqi <= 100: return "Moderate"
    elif aqi <= 150: return "Unhealthy for Sensitive Groups"
    elif aqi <= 200: return "Unhealthy"
    elif aqi <= 300: return "Very Unhealthy"
    else: return "Hazardous"

df['Category'] = df['AQI'].apply(get_aqi_category)
print("\nAQI Category Distribution:")
print(df['Category'].value_counts())
