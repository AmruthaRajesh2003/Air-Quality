# 🌿 Real-Time Air Quality Monitoring System



![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)




![ESP32](https://img.shields.io/badge/Hardware-ESP32-blue?logo=espressif&logoColor=white)




![Flask](https://img.shields.io/badge/Flask-REST%20API-000000?logo=flask&logoColor=white)




![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit&logoColor=white)




![MySQL](https://img.shields.io/badge/MySQL-Database-4479A1?logo=mysql&logoColor=white)




![Arduino](https://img.shields.io/badge/Arduino-IDE-00979D?logo=arduino&logoColor=white)



---

## 📌 Project Overview

**Real-Time Air Quality Monitoring System** is an IoT-based project that continuously
monitors environmental air quality parameters and displays live data through a Python
dashboard. The system uses an **ESP32 microcontroller** paired with **MQ-series gas sensors**
to detect harmful pollutants and triggers alerts when values exceed safe thresholds.

---

## 🔧 Tech Stack

| Layer | Tools |
|-------|-------|
| 

![Hardware](https://img.shields.io/badge/Hardware-ESP32-blue?logo=espressif&logoColor=white)

 | ESP32 Microcontroller |
| 

![Sensor](https://img.shields.io/badge/Sensor-MQ--135-brightgreen)

 | MQ-135 / MQ-2 Gas Sensor |
| 

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)

 | Backend & Data Processing |
| 

![Flask](https://img.shields.io/badge/Flask-REST%20API-000000?logo=flask&logoColor=white)

 | API Communication |
| 

![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit&logoColor=white)

 | Live Dashboard |
| 

![MySQL](https://img.shields.io/badge/MySQL-Database-4479A1?logo=mysql&logoColor=white)

 | Data Logging |
| 

![Arduino](https://img.shields.io/badge/Arduino-IDE-00979D?logo=arduino&logoColor=white)

 | ESP32 Programming |
| 

![WiFi](https://img.shields.io/badge/Protocol-HTTP%2FMQTT-8A2BE2)

 | Data Transmission |

---

## 🌟 Key Features

- 📡 Real-time sensor data collection via ESP32
- 📊 Live air quality dashboard with graphs and visualizations
- ⚠️ Threshold-based alert system for dangerous pollution levels
- 🌡️ Temperature and humidity monitoring (DHT11)
- 💾 Data logging for historical analysis
- 🔌 Wi-Fi enabled data transmission (HTTP/MQTT)

---

## 🏗️ System Architecture

MQ-135 Sensor ──┐
MQ-2 Sensor  ──┤──► ESP32 ──► Wi-Fi ──► Flask API ──► MySQL Database
DHT11 Sensor ──┘                                  └──► Streamlit Dashboard
---

## ⚙️ How It Works

1. **Sensors** continuously measure air quality parameters (CO2, smoke, dust, temperature, humidity)
2. **ESP32** reads sensor data and transmits it over Wi-Fi using HTTP/MQTT protocol
3. **Flask API** receives and processes the incoming sensor data
4. **MySQL** stores the data for historical analysis and logging
5. **Streamlit Dashboard** visualizes live and historical data with real-time graphs
6. **Alert System** triggers notifications when pollution levels cross safe thresholds

---

## 📊 Monitored Parameters

| Parameter | Sensor | Safe Threshold |
|-----------|--------|----------------|
| CO2 / Smoke | MQ-2 | < 300 ppm |
| Air Quality Index | MQ-135 | < 100 AQI |
| Temperature | DHT11 | 18°C – 35°C |
| Humidity | DHT11 | 30% – 70% |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.x
- Arduino IDE (for ESP32 programming)
- MySQL Server

### Installation

```bash
# Clone the repository
git clone https://github.com/AmruthaRajesh2003/real-time-air-quality-monitoring.git
cd real-time-air-quality-monitoring

# Install dependencies
pip install -r requirements.txt

# Run the Flask API
python app.py

# Run the Streamlit Dashboard
streamlit run dashboard.py
