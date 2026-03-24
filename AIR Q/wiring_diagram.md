# Wiring Diagram & Instructions
# Board: ESP32-WROOM-32UE (ESP32S)

## Components Required
1.  **ESP32-WROOM-32UE** Dev Board
2.  **MQ-2 Gas Sensor** (LPG, Smoke)
3.  **DHT11** or **DHT22** (Temperature & Humidity)
4.  Jumper Wires
5.  Breadboard
6.  USB-C Cable for Power/Programming

## Wiring Connections

### 1. MQ-2 Gas Sensor
| MQ-2 Pin | ESP32 Board Label | Description |
| :--- | :--- | :--- |
| **VCC** | **5V** (bottom-left pin) | MQ-2 heater needs 5V. Use the `5V` pin on board. |
| **GND** | **GND** | Any GND pin on the board. |
| **A0 (Analog)** | **34** (left side, 3rd from top after VP/VN) | Analog Input only pin. Safe for ADC. |
| **D0 (Digital)** | Not Connected | Using Analog (A0) for precision readings. |

> **Important**: The `34` pin on this board is **input-only** (no internal pull-up/pull-down). It is safe for ADC analog reading. The MQ-2 A0 output must NOT exceed **3.3V** into pin 34. Since MQ-2 is powered by 5V, its A0 can output up to ~4V. Add a **voltage divider** for safety:
> - Connect MQ-2 A0 → 10kΩ resistor → pin `34`
> - Connect junction of 10kΩ and 20kΩ to pin `34`, other end of 20kΩ to GND.

### 2. DHT11 / DHT22 Sensor
| DHT Pin | ESP32 Board Label | Description |
| :--- | :--- | :--- |
| **VCC** | **3V3** (top-left pin) | 3.3V power supply. |
| **GND** | **GND** | Any GND pin on the board. |
| **DATA** | **4** (right side) | Digital GPIO pin. |

> **Note**: If using a bare DHT sensor (not a module), add a **10kΩ pull-up resistor** between VCC and DATA. Most breakout modules have this built-in.

---

## Board Pin Reference (ESP32-WROOM-32UE)

```
LEFT SIDE (top to bottom)     RIGHT SIDE (top to bottom)
----------------------------  ----------------------------
3V3  <- DHT VCC               GND
EN                            23
VP  (GPIO 36, input-only)     22
VN  (GPIO 39, input-only)     TX
34  <- MQ-2 A0                RX
35                            21
32                            GND
33                            19
25                            18
26                            5
27                            17
14                            16
12                            4  <- DHT DATA
GND                           0
13                            2
D2  [DO NOT USE - Flash]      15
D3  [DO NOT USE - Flash]      CLK  [DO NOT USE - Flash]
CMD [DO NOT USE - Flash]      D0   [DO NOT USE - Flash]
5V  <- MQ-2 VCC               D1   [DO NOT USE - Flash]
                              Boot [Button]
```

> ⚠️ **Warning**: Do NOT use pins labeled `D0, D1, D2, D3, CMD, CLK` — these are connected to internal Flash memory and will cause boot failures.

---

## Code Configuration

1.  Open `esp32_firmware.ino`.
2.  Update `ssid` and `password` with your Wi-Fi credentials.
3.  Find your computer's local IP: run `ipconfig` in Command Prompt.
4.  Update `serverUrl`:
    ```cpp
    const char* serverUrl = "http://192.168.1.100:5000/api/data";
    ```
5.  Upload to ESP32.

## Running the System

1.  Start API Server on your PC:
    ```bash
    python api_server.py
    ```
2.  Power on ESP32 via USB-C.
3.  Open **Serial Monitor** at **115200 baud** to see readings.
