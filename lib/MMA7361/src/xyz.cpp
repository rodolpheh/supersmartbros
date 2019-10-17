#include "xyz.h"

void xyz_print(xyz xyzzie) {
  Serial.print("X: ");
  Serial.println(xyzzie.x);
  Serial.print("Y: ");
  Serial.println(xyzzie.y);
  Serial.print("Z: ");
  Serial.println(xyzzie.z);
}

void xyz_print(xyz_voltage xyzzie) {
  Serial.print("X: ");
  Serial.println(xyzzie.x);
  Serial.print("Y: ");
  Serial.println(xyzzie.y);
  Serial.print("Z: ");
  Serial.println(xyzzie.z);
}

int xyz_magnitude(xyz xyzzie) {
  return (int)sqrt((xyzzie.x^2) + (xyzzie.y^2) + (xyzzie.z^2));
}

xyz xyz_normalize(xyz xyzzie) {
  int magnitude = xyz_magnitude(xyzzie);
  return (xyz) {
    xyzzie.x - magnitude,
    xyzzie.y - magnitude,
    xyzzie.z - magnitude
  };
}

xyz_voltage xyz_to_voltage(xyz xyzzie, float vcc) {
  return (xyz_voltage) {
    (float)xyzzie.x / 4096 * 3.3f,
    (float)xyzzie.y / 4096 * 3.3f,
    (float)xyzzie.z / 4096 * 3.3f
  };
}