#include <Arduino.h>
#include "../src/dummyLib.hpp"

void setup() {
    Serial.begin(115200);
    Serial.println(dummyFunction());
}

void loop() {
}