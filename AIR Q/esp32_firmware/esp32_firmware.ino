#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

#define MQ2 A0

const char* ssid = "RedmiNote10Pro";
const char* password = "Akhiljoji1451";

String apiKey = "a2328168f61d326117a9c7cb14469d94";
String city = "Ettumanoor";
String country = "IN";

String serverUrl = "http://10.245.201.34:5000/api/data";   // change this

WiFiClient client;

void setup() {
  Serial.begin(9600);

  WiFi.begin(ssid, password);
  Serial.print("Connecting");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected ✅");
}

void loop() {

  int gasValue = analogRead(MQ2);

  if (WiFi.status() == WL_CONNECTED) {

    // ---------- GET WEATHER ----------
    HTTPClient http;
    String url = "http://api.openweathermap.org/data/2.5/weather?q=" + city + "," + country + "&appid=" + apiKey + "&units=metric";

    http.begin(client, url);
    int httpCode = http.GET();

    float temp = 0;
    float hum  = 0;

    if (httpCode > 0) {
      String payload = http.getString();

      DynamicJsonDocument doc(1024);
      deserializeJson(doc, payload);

      temp = doc["main"]["temp"];
      hum  = doc["main"]["humidity"];

      Serial.println("\n------ Live Data ------");
      Serial.print("MQ2 Gas: ");
      Serial.println(gasValue);

      Serial.print("Temp(API): ");
      Serial.println(temp);

      Serial.print("Humidity(API): ");
      Serial.println(hum);
    } else {
      Serial.println("Weather API Failed ❌");
    }

    http.end();

    // ---------- POST TO FLASK ----------
    HTTPClient httpPost;
    httpPost.begin(client, serverUrl);
    httpPost.addHeader("Content-Type", "application/json");

    String jsonBody = "{\"temperature\":" + String(temp) +
                      ",\"humidity\":"    + String(hum)  +
                      ",\"mq2_value\":"   + String(gasValue) + "}";

    int postCode = httpPost.POST(jsonBody);

    if (postCode > 0) {
      Serial.print("Server Response: ");
      Serial.println(httpPost.getString());
    } else {
      Serial.println("POST Failed ❌");
    }

    httpPost.end();
  }

  delay(5000);
}