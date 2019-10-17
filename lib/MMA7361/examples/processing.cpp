#include <Arduino.h>
#include "MMA7361.h"
#include "xyz.h"

void setup() {
  Serial.begin(115200);
}

void loop() {
  xyz values = MMA7361_getValues();
  xyz_voltage voltages = xyz_to_voltage(values, 3.3);
  xyz_print(voltages);
  delay(100);
}