#include <Arduino.h>
#include <tilt-sensor.h>

#define TILT_PIN 13

void setup() {
  Serial.begin(115200);
  setup_tilt();
}

void loop() {
  if (was_triggered()) {
    Serial.println("Jump !");
  }
  delay(20);
}