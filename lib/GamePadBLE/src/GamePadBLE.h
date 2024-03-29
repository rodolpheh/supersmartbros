#ifndef GAMEPADBLE_H_
#define GAMEPADBLE_H_

#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
#include "BLE2902.h"
#include "BLEHIDDevice.h"
#include "HIDTypes.h"
//#include "HIDKeyboardTypes.h"
#include <driver/adc.h>
#include "keymaps.h"

enum Controls
{
    LEFT,
    RIGHT,
    UP,
    DOWN,
    A,
    B,
    SELECT,
    START
};


extern bool connected;
extern BLECharacteristic* pTxCharacteristic;
extern BLECharacteristic* pRxCharacteristic;
extern std::string rxValue;

void taskServer(void*);

void initGamePad(const char* left, const char* right, const char* up, const char* down,
                 const char* A, const char* B, const char* start, const char* select);

void press(Controls direction);
void release();
void pressForSeconds(Controls direction, float seconds);
void sendTrame(uint8_t * chars);

#endif