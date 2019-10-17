# Super Smart Bros

In this project, we will use an ESP32 as a Bluetooth controller to play Super Mario Bros on a NES emulator.

## Hardware

* ESP32
* Tilt sensor
* Triple-axis accelerometer
* Proximity sensor
* Screen
* USB battery

## Software

* PlatformIO: ESP32 development (necessary for building)
* FCEUX: NES emulator, includes a Lua interpreter (use Windows version in Wine for UNIX and Linux systems)

## Build and upload

```bash
platformio run --target upload
```

## Build and upload library example

```bash
./build-example.sh DummyLib dummyExample.cpp

# Or for the debug build:
./build-example.sh DummyLib dummyExample.cpp debug
```