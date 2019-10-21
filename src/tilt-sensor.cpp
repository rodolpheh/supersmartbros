#include "tilt-sensor.h"

bool was_triggered() {
  static int val;
  static bool hasBeenTriggered;
  val = digitalRead(TILT_PIN);
  if (true == hasBeenTriggered) {
    if (HIGH == val) {
      hasBeenTriggered = false;
    }
  } else {
    if (LOW == val){
        hasBeenTriggered = true;
        return true;
      }
  }
  return false;
}

void setup_tilt() {
  pinMode(TILT_PIN, INPUT);
  digitalWrite(TILT_PIN, LOW);
}