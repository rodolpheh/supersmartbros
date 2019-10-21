#include <Arduino.h>
#include <GamePadBLE.h>
#include <MMA7361.h>
#include <tilt-sensor.h>

int value = 0;
bool pressed = false;
bool jumped = false;

Controls controls[3];

unsigned long now = millis();
unsigned long until = now + 500;

void setup() {
  Serial.begin(115200);
  initGamePad("q","d", "z", "s","a","e","o", "p");
  setup_tilt();
}

void loop() {
  xyz orientation = MMA7361_getValues();

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
      press(Controls::RIGHT);
      Serial.println("Press right !");
      pressed = true;
    }
  }
  else if (orientation.y < 1500) {
    if (!pressed) {
      press(Controls::LEFT);
      Serial.println("Press left !");
      pressed = true;
    }
  }
  else {
    if (pressed) {
      release();
      Serial.println("Release !");
      pressed = false;
    }
  }

  if (now > until) {
    if (jumped) {
      release();
      Serial.println("Release !");
      jumped = false;
    }
    if (was_triggered()) {
      now = millis();
      until = now + 2000;
      if (!jumped) {
        press(Controls::UP);
        Serial.println("Jump!");
        jumped = true;
      }
    }
  }

  now = millis();

  vTaskDelay(1);
}