"""
train_model.py
──────────────
Trains an ML classifier using REAL IoT readings (air_quality_db.readings.csv)
with a physics-based AQI formula as the labelling engine.

AQI Formula:
  Gas_norm = (gas_raw / 1023) * 100          # normalize to 0-100%
  AQI      = 0.6*Gas_norm + 0.25*Humidity + 0.15*Temperature

AQI Categories:
  0  – 50   → Good
  51 – 100  → Moderate
  101– 150  → Poor
  151– 200  → Very Poor
  201+      → Hazardous

Features  : gas_raw, temperature, humidity
Target    : AQI category (derived above)
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import pickle

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
READINGS_CSV = os.path.join(BASE_DIR, "air_quality_db.readings.csv")
MODEL_PATH   = os.path.join(BASE_DIR, "air_quality_model.pkl")

print("=" * 55)
print("  Air Quality ML Trainer  (AQI Formula Labels)")
print("=" * 55)

# ── AQI helpers ───────────────────────────────────────────────────────────
def compute_aqi(gas_raw, humidity, temperature):
    gas_norm = (gas_raw / 1023.0) * 100.0
    return (0.6 * gas_norm) + (0.25 * humidity) + (0.15 * temperature)

def aqi_to_category(aqi):
    if aqi <= 50:   return "Good"
    elif aqi <= 100: return "Moderate"
    elif aqi <= 150: return "Poor"
    elif aqi <= 200: return "Very Poor"
    else:            return "Hazardous"

# ── Load real IoT readings ────────────────────────────────────────────────
df = pd.read_csv(READINGS_CSV)
df = df[["temperature", "humidity", "gas_raw"]].dropna()
print(f"\nLoaded {len(df)} real sensor readings.")
print(f"  gas_raw    : {df['gas_raw'].min():.0f} – {df['gas_raw'].max():.0f}")
print(f"  temperature: {df['temperature'].min():.1f} – {df['temperature'].max():.1f} C")
print(f"  humidity   : {df['humidity'].min():.1f} – {df['humidity'].max():.1f} %")

# ── Compute AQI and labels on real data ───────────────────────────────────
df["aqi"]      = df.apply(lambda r: compute_aqi(r.gas_raw, r.humidity, r.temperature), axis=1)
df["category"] = df["aqi"].apply(aqi_to_category)

print(f"\nReal data AQI range: {df['aqi'].min():.1f} – {df['aqi'].max():.1f}")
print(f"\nReal data label distribution:")
print(df["category"].value_counts().to_string())

# ── Augment data to cover the full AQI range ──────────────────────────────
np.random.seed(42)

real_temp_mean = float(df["temperature"].mean())
real_hum_mean  = float(df["humidity"].mean())

def make_samples(n, gas_lo, gas_hi, label):
    rows = []
    for _ in range(n):
        gas  = np.random.uniform(gas_lo, gas_hi)
        temp = real_temp_mean + np.random.normal(0, 3)
        hum  = np.clip(real_hum_mean  + np.random.normal(0, 8), 0, 100)
        aqi  = compute_aqi(gas, hum, temp)
        rows.append({
            "gas_raw": round(gas, 0),
            "temperature": round(temp, 2),
            "humidity": round(hum, 2),
            "aqi": round(aqi, 2),
            "category": aqi_to_category(aqi)
        })
    return pd.DataFrame(rows)

# Cover each tier proportionally
extra = pd.concat([
    make_samples(400,   0,  420, "Good"),       # AQI 0-50
    make_samples(400, 430,  760, "Moderate"),   # AQI 51-100
    make_samples(300, 770,  930, "Poor"),        # AQI 101-150
    make_samples(200, 940, 1000, "Very Poor"),  # AQI 151-200
    make_samples(100,1001, 1023, "Hazardous"),  # AQI 200+
], ignore_index=True)

df_full = pd.concat([df, extra], ignore_index=True).sample(frac=1, random_state=42)
print(f"\nAugmented dataset: {len(df_full)} rows")
print(df_full["category"].value_counts().to_string())

# ── Train ──────────────────────────────────────────────────────────────────
X = df_full[["gas_raw", "temperature", "humidity"]]
y = df_full["category"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("\nTraining RandomForestClassifier...")
clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)
acc    = accuracy_score(y_test, y_pred)
print(f"Accuracy: {acc:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# ── Save ───────────────────────────────────────────────────────────────────
with open(MODEL_PATH, "wb") as f:
    pickle.dump(clf, f)

print(f"\nModel saved -> {MODEL_PATH}")
print("\nFeatures  : [gas_raw, temperature, humidity]")
print("AQI Formula: 0.6*(gas_raw/1023*100) + 0.25*Humidity + 0.15*Temperature")
print("Labels    : Good(0-50) | Moderate(51-100) | Poor(101-150) | Very Poor(151-200) | Hazardous(200+)")
