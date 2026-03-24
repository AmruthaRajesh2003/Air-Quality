import os
from flask import Flask, request, jsonify
from datetime import datetime
import socket
import pickle
import pandas as pd
from db_handler import get_collection, save_reading

# --- Configuration ---
MODEL_PATH = os.path.join(os.path.dirname(__file__), "air_quality_model.pkl")

app = Flask(__name__)

# --- Auto-detect local IP for display ---
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# --- Load ML Model ---
def load_model():
    try:
        with open(MODEL_PATH, "rb") as f:
            m = pickle.load(f)
        print("[ML] Model loaded successfully.")
        return m
    except FileNotFoundError:
        print("[ML] Model file not found. ML predictions will be skipped.")
        return None
    except Exception as e:
        print(f"[ML] Failed to load model: {e}")
        return None

model = load_model()

# --- Helper functions ---
def compute_aqi(gas_raw: int, humidity: float, temperature: float) -> float:
    """
    AQI Formula:
      Gas_norm = (gas_raw / 1023) * 100
      AQI = 0.6*Gas_norm + 0.25*Humidity + 0.15*Temperature
    """
    gas_norm = (gas_raw / 1023.0) * 100.0
    return round((0.6 * gas_norm) + (0.25 * humidity) + (0.15 * temperature), 2)

def aqi_to_category(aqi: float) -> str:
    if aqi <= 50:    return "Good"
    elif aqi <= 100: return "Moderate"
    elif aqi <= 150: return "Poor"
    elif aqi <= 200: return "Very Poor"
    else:            return "Hazardous"

def get_rule_based_category(gas_val: int, temp: float = 0, hum: float = 0):
    """Rule-based AQI classification using weighted formula."""
    aqi = compute_aqi(gas_val, hum, temp)
    return aqi_to_category(aqi), aqi

def run_ml_prediction(mq2_raw: int, temp: float, hum: float) -> str:
    """
    ML prediction using features: [gas_raw, temperature, humidity]
    Model trained on real IoT readings labelled via AQI formula.
    Labels: Good / Moderate / Poor / Very Poor / Hazardous
    """
    if model is None:
        return "N/A"
    try:
        input_df = pd.DataFrame(
            [[mq2_raw, temp, hum]],
            columns=["gas_raw", "temperature", "humidity"]
        )
        return model.predict(input_df)[0]
    except Exception as e:
        print(f"[ML] Prediction error: {e}")
        return "Error"

# =====================================================================
# --- ROUTES ---
# =====================================================================

@app.route("/api/data", methods=["POST"])
def receive_data():
    """Receive sensor data from the ESP32 and store it in MongoDB."""
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "No JSON body received"}), 400

        # Validate required fields
        required = ["temperature", "humidity", "mq2_value"]
        missing = [k for k in required if k not in data]
        if missing:
            return jsonify({"error": f"Missing fields: {missing}"}), 400

        temp    = float(data["temperature"])
        hum     = float(data["humidity"])
        mq2_raw = int(data["mq2_value"])

        rule_cat, rule_score = get_rule_based_category(mq2_raw, temp, hum)

        reading = {
            "timestamp":     datetime.now(),
            "temperature":   temp,
            "humidity":      hum,
            "gas_raw":       mq2_raw,
            "rule_category": rule_cat,
        }

        success, msg = save_reading(reading)
        if success:
            print(f"[DATA] Temp={temp}C  Hum={hum}%  MQ2={mq2_raw}  -> {rule_cat}")
            return jsonify({
                "status":   "success",
                "category": rule_cat,
            }), 200
        else:
            return jsonify({"status": "error", "message": msg}), 500

    except Exception as e:
        print(f"[ERROR] /api/data -> {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/latest", methods=["GET"])
def latest_reading():
    """Return the most recent sensor reading (useful for quick checks)."""
    col = get_collection()
    if col is None:
        return jsonify({"error": "Database not connected"}), 500
    try:
        doc = col.find_one(sort=[("timestamp", -1)])
        if doc:
            doc["_id"] = str(doc["_id"])
            if "timestamp" in doc:
                doc["timestamp"] = doc["timestamp"].isoformat()
            return jsonify(doc), 200
        return jsonify({"message": "No data yet"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint — verify server, DB, and model status."""
    col = get_collection()
    db_status = "connected" if col is not None else "disconnected"
    ml_status = "loaded"    if model is not None else "not loaded"
    ip        = get_local_ip()
    return jsonify({
        "server":      "running",
        "database":    db_status,
        "model":       ml_status,
        "local_ip":    ip,
        "esp32_target": f"http://{ip}:5000/api/data",
    }), 200


if __name__ == "__main__":
    ip = get_local_ip()
    print("=" * 55)
    print("  Air Quality API Server")
    print(f"  Local IP   : {ip}")
    print(f"  Health     : http://{ip}:5000/health")
    print(f"  ESP32 POST : http://{ip}:5000/api/data")
    print("=" * 55)
    app.run(host="0.0.0.0", port=5000, debug=False)
