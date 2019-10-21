#include <Arduino.h>
#include <GamePadBLE.h>
#include <MMA7361.h>
#include <Screen.h>

int value = 0;

void setup() {
  Serial.begin(115200);
  initGamePad("q","d", "z", "s","a","e","o", "p");
  init();
  //pressForSeconds(Controls::RIGHT, 2.0);
}

void loop() {
  xyz orientation = MMA7361_getValues();

  //press(Controls::A);
  //press(Controls::A);
  //press(Controls::B);
  //press(Controls::B);
  //press(Controls::DOWN);
  //press(Controls::UP);
  Serial.print("UP from classic serial: ");
  Serial.println(value);
  if (connected) {
    pTxCharacteristic->setValue(value);
    pTxCharacteristic->notify();
    delay(10); // bluetooth stack will go into congestion, if too many packets are sent
    value++;
  }

  Serial.print("rxValue :");
  Serial.println(rxValue.c_str());
  //press(Controls::UP);
  //press(Controls::RIGHT);
  vTaskDelay(500);
}