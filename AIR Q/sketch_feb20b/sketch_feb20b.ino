#include <dummy.h>

// ESP32 Basic Working Test
// Most ESP32 dev boards use GPIO 2 for the built-in LED
const int ledPin = 2; 

void setup() {
  // Initialize Serial Monitor
  Serial.begin(115200);
  // Initialize LED pin as output
  pinMode(ledPin, OUTPUT);
  Serial.println("ESP32 Starting...");
}

void loop() {
  digitalWrite(ledPin, HIGH);   // Turn LED on
  Serial.println("LED: ON");
  delay(1000);                  // Wait 1 second
  digitalWrite(ledPin, LOW);    // Turn LED off
  Serial.println("LED: OFF");
  delay(1000);                  // Wait 1 second
}
