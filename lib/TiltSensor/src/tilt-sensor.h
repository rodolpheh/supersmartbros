#ifndef TILT_SENSOR_H
#define TILT_SENSOR_H

#include <Arduino.h>

#ifndef TILT_PIN
  #define TILT_PIN 13
#endif

bool was_triggered();

void setup_tilt();

#endif