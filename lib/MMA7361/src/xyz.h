#ifndef XYZ_H_
#define XYZ_H_

#include <Arduino.h>
#include <math.h>

typedef struct _xyz {
  int x;
  int y;
  int z;
} xyz;

typedef struct _xyz_voltage {
  float x;
  float y;
  float z;
} xyz_voltage;

void xyz_print(xyz xyzzie);
void xyz_print(xyz_voltage xyzzie);
int xyz_magnitude(xyz xyzzie);
xyz xyz_normalize(xyz xyzzie);
xyz_voltage xyz_to_voltage(xyz xyzzie, float vcc);

#endif