
import csv
import statistics

filename = 'e:\\Air Quality\\global_air_quality_dataset.csv'

def calculate_stats(values, name):
    if not values:
        print(f"\nStats for {name}: No data found.")
        return
    print(f"\nStats for {name}:")
    print(f"  Count: {len(values)}")
    print(f"  Min: {min(values)}")
    print(f"  Max: {max(values)}")
    print(f"  Mean: {statistics.mean(values):.2f}")
    if len(values) > 1:
        print(f"  StdDev: {statistics.stdev(values):.2f}")

try:
    with open(filename, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        print("Columns:", header)
        
        # Find indices
        temp_idx = -1
        hum_idx = -1
        co_idx = -1
        aqi_idx = -1
        
        for i, col in enumerate(header):
            if 'Temperature' in col: temp_idx = i
            if 'Humidity' in col: hum_idx = i
            if 'CO ' in col or col == 'CO': co_idx = i  # Check for CO specifically
            if 'AQI' in col: aqi_idx = i
        
        # Also check for CO with units like "CO (ppm)"
        if co_idx == -1:
             for i, col in enumerate(header):
                if 'CO' in col and 'Country' not in col: # Avoid Country
                    co_idx = i

        print(f"Indices: Temp={temp_idx}, Hum={hum_idx}, CO={co_idx}, AQI={aqi_idx}")
        
        temps = []
        hums = []
        cos = []
        aqis = []
        
        for row in reader:
            try:
                if temp_idx != -1 and row[temp_idx]: temps.append(float(row[temp_idx]))
                if hum_idx != -1 and row[hum_idx]: hums.append(float(row[hum_idx]))
                if co_idx != -1 and row[co_idx]: cos.append(float(row[co_idx]))
                if aqi_idx != -1 and row[aqi_idx]: aqis.append(float(row[aqi_idx]))
            except ValueError:
                continue # Skip bad rows

        calculate_stats(temps, "Temperature")
        calculate_stats(hums, "Humidity")
        calculate_stats(cos, "CO")
        calculate_stats(aqis, "AQI")

        # Categorize AQI
        categories = {'Good': 0, 'Moderate': 0, 'Unhealthy Sens.': 0, 'Unhealthy': 0, 'Very Unhealthy': 0, 'Hazardous': 0}
        for aqi in aqis:
            if aqi <= 50: categories['Good'] += 1
            elif aqi <= 100: categories['Moderate'] += 1
            elif aqi <= 150: categories['Unhealthy Sens.'] += 1
            elif aqi <= 200: categories['Unhealthy'] += 1
            elif aqi <= 300: categories['Very Unhealthy'] += 1
            else: categories['Hazardous'] += 1
            
        print("\nAQI Categories Distribution:")
        for k, v in categories.items():
            print(f"  {k}: {v}")

except Exception as e:
    print(f"Error: {e}")
