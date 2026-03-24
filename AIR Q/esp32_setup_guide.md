# ESP32 Setup & Library Installation Guide

## Required Libraries (Install These First!)

### DHT Sensor Library (REQUIRED)
1. In Arduino IDE, go to **Sketch** → **Include Library** → **Manage Libraries...**
2. Search: `DHT sensor library`
3. Find **"DHT sensor library"** by **Adafruit** → click **Install**
4. A popup will appear asking about dependencies → click **"Install All"**

If the above doesn't work, try searching just `DHT` and look for the Adafruit one.

---

### Alternative: Manual Install (if Manage Libraries fails)
1. Download ZIP from: https://github.com/adafruit/DHT-sensor-library/archive/refs/heads/master.zip
2. In Arduino IDE: **Sketch** → **Include Library** → **Add .ZIP Library...**
3. Select the downloaded ZIP file → done.
4. Also download and add: https://github.com/adafruit/Adafruit_Sensor/archive/refs/heads/master.zip

---

## Board Manager Setup

### Step 1: Add ESP32 Board URL
1. Go to **File** → **Preferences**
2. In "Additional Boards Manager URLs", add:
    ```
    https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
    ```
3. Click **OK**

### Step 2: Install ESP32 Board Package
1. Go to **Tools** → **Board** → **Boards Manager...**
2. Search `esp32`
3. Install **"esp32 by Espressif Systems"**

### Step 3: Select Board & Port
1. **Tools** → **Board** → **ESP32 Arduino** → **DOIT ESP32 DEVKIT V1**
2. **Tools** → **Port** → Select your COM port

### Step 4: Upload
1. Open `esp32_firmware.ino`
2. Click **Upload** (→ arrow)
3. If "Connecting..." hangs → hold the **BOOT** button on the board until it starts uploading
