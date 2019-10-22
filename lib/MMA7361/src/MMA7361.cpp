#include "MMA7361.h"

xyz MMA7361_getRawValues() {
  return (xyz) {
    analogRead(X_PIN),
    analogRead(Y_PIN),
    analogRead(Z_PIN)
  };
}

xyz MMA7361_getValues() {
  // Compensate badly calibrated chip
  int x_offset = (X_VALUE_AT_0G - SUPPOSED_X_VALUE_AT_0G) / 3.3 * 4096;
  int y_offset = (Y_VALUE_AT_0G - SUPPOSED_Y_VALUE_AT_0G) / 3.3 * 4096;
  int z_offset = (Z_VALUE_AT_1G - SUPPOSED_Z_VALUE_AT_1G) / 3.3 * 4096;

  return (xyz) {
    analogRead(X_PIN) - x_offset,
    analogRead(Y_PIN) - y_offset,
    analogRead(Z_PIN) - z_offset
  };
}