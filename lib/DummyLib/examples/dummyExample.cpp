#include <Arduino.h>
#include "../src/dummyLib.hpp"

void setup() {
    Serial.begin(9600);
    Serial.println(dummyFunction());
}

void loop() {
}