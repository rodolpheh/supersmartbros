#include <Arduino.h>
#include "GamePadBLE.h"
void setup() {
  Serial.begin(115200);
  initGamePad("q","d", "z", "s","a","e","o", "p");
}

void loop() {
  //press(Controls::A);
  //press(Controls::A);
  //press(Controls::B);
  //press(Controls::B);
  //press(Controls::DOWN);
  //press(Controls::UP);
  Serial.print("UP");
  //press(Controls::UP);
  //press(Controls::RIGHT);
  vTaskDelay(5000);
}