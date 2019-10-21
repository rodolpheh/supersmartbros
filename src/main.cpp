#include <Arduino.h>
#include <GamePadBLE.h>
#include <MMA7361.h>
#include <tilt-sensor.h>

#define PROXIMITY_SENSOR 33

int value = 0;
bool pressed = false;
bool jumped = false;
bool runned = false;

uint8_t trame[] = {0x0, 0x0, 0x0};
bool trame_changed = false;

unsigned long now = millis();
unsigned long until = now + 500;

void setup() {
  Serial.begin(115200);
  initGamePad("q","d", "z", "s","a","e","o", "p");
  setup_tilt();
  pinMode(PROXIMITY_SENSOR, INPUT);
}

void loop() {
  xyz orientation = MMA7361_getRawValues();

  //press(Controls::A);
  //press(Controls::B);
  //press(Controls::DOWN);
  //press(Controls::UP);
  //press(Controls::RIGHT);
  //press(Controls::LEFT);

  // Serial.print("X: ");
  // Serial.print(orientation.x);
  // Serial.print(", Y: ");
  // Serial.print(orientation.y);
  // Serial.print(", Z: ");
  // Serial.println(orientation.z);

  if (orientation.y > 2500) {
    if (!pressed) {
      // press(Controls::RIGHT);
      trame[0] = 'd';
      trame_changed = true;
      Serial.println("Press right !");
      pressed = true;
    }
  }
  else if (orientation.y < 1500) {
    if (!pressed) {
      // press(Controls::LEFT);
      trame[0] = 'q';
      trame_changed = true;
      Serial.println("Press left !");
      pressed = true;
    }
  }
  else {
    if (pressed) {
      // release();
      trame[0] = 0x0;
      trame_changed = true;
      Serial.println("Release !");
      pressed = false;
    }
  }

  if (now > until) {
    if (jumped) {
      // release();
      trame[1] = 0x0;
      trame_changed = true;
      Serial.println("Release !");
      jumped = false;
    }
    if (was_triggered()) {
      now = millis();
      until = now + 500;
      if (!jumped) {
        // press(Controls::UP);
        trame[1] = 'z';
        trame_changed = true;
        Serial.println("Jump!");
        jumped = true;
      }
    }
  }

  if (!runned && !digitalRead(PROXIMITY_SENSOR)) {
    trame[2] = 'm';
    trame_changed = true;
    runned = true;
  }
  else if (runned && digitalRead(PROXIMITY_SENSOR)) {
    trame[2] = 0x0;
    trame_changed = true;
    runned = false;
  }

  now = millis();

  if (trame_changed) {
    sendTrame(trame);
    trame_changed = false;
  }

  vTaskDelay(1);
}