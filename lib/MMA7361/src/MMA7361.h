#ifndef MMA7361_H_
#define MMA7361_H_

#include <Arduino.h>
#include <xyz.h>

#define X_PIN 34
#define Y_PIN 35
#define Z_PIN 32

#define X_VALUE_AT_0G 1.36
#define Y_VALUE_AT_0G 1.51
#define Z_VALUE_AT_1G 1.92

#define SUPPOSED_X_VALUE_AT_0G 1.65
#define SUPPOSED_Y_VALUE_AT_0G 1.65
#define SUPPOSED_Z_VALUE_AT_1G 2.45

#define X_VALUE_AT_1G 2.4
#define Y_VALUE_AT_1G 2.4

#define X_VALUE_AT_MINUS_1G 0.9
#define Y_VALUE_AT_MINUS_1G 0.9

#define SUPPOSED_X_VALUE_AT_1G 2.75
#define SUPPOSED_Y_VALUE_AT_1G 2.75

#define SUPPOSED_X_VALUE_AT_MINUS_1G 0.55
#define SUPPOSED_Y_VALUE_AT_MINUS_1G 0.55

xyz MMA7361_getValues();

#endif