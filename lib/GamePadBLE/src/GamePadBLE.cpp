#include "GamePadBLE.h"

#define SERVICE_UART_UUID      "6E400001-B5A3-F393-E0A9-E50E24DCCA9E" // UART service UUID
#define CHARACTERISTIC_UUID_RX "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
#define CHARACTERISTIC_UUID_TX "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

BLECharacteristic* pTxCharacteristic = NULL;
BLECharacteristic* pRxCharacteristic = NULL;
std::string rxValue = "0-1;09;69;6969696;0;";
const char* keyControls[8] = {"q","d","z","s","a","e","o","p"};
BLEHIDDevice* hid;
BLECharacteristic* input;
BLECharacteristic* output;
BLEService* readService;

uint8_t buttons = 0;
uint8_t button1 = 0;
uint8_t button2 = 0;
uint8_t button3 = 0;
bool connected = false;

class MyCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer* pServer){
    connected = true;
    BLE2902* desc = (BLE2902*)input->getDescriptorByUUID(BLEUUID((uint16_t)0x2902));
    desc->setNotifications(true);
  }

  void onDisconnect(BLEServer* pServer){
    connected = false;
    BLE2902* desc = (BLE2902*)input->getDescriptorByUUID(BLEUUID((uint16_t)0x2902));
    desc->setNotifications(false);
  }
};

/*
 * This callback is connect with output report. In keyboard output report report special keys changes, like CAPSLOCK, NUMLOCK
 * We can add digital pins with LED to show status
 * bit 0 - NUM LOCK
 * bit 1 - CAPS LOCK
 * bit 2 - SCROLL LOCK
 */
 class MyOutputCallbacks : public BLECharacteristicCallbacks {
 void onWrite(BLECharacteristic* me){
    uint8_t* value = (uint8_t*)(me->getValue().c_str());
    ESP_LOGI(LOG_TAG, "special keys: %d", *value);

    rxValue = me->getValue();

    if (rxValue.length() > 0)
    {
      Serial.println("*********");
      Serial.print("Received Value: ");
      for (int i = 0; i < rxValue.length(); i++){
        Serial.print(rxValue[i]);
      }
      Serial.println();
      Serial.println("*********");
    }
  }
};

void taskServer(void*){
    BLEDevice::init("GamePad Mario");
    BLEServer *pServer = BLEDevice::createServer();
    pServer->setCallbacks(new MyCallbacks());

    hid = new BLEHIDDevice(pServer);
    input = hid->inputReport(1); // <-- input REPORTID from report map
    output = hid->outputReport(1); // <-- output REPORTID from report map
    output->setReadProperty(true);
    output->setCallbacks(new MyOutputCallbacks());

    std::string name = "PENISEN";
    hid->manufacturer()->setValue(name);

    hid->pnp(0x02, 0xe502, 0xa111, 0x0210);
    hid->hidInfo(0x00,0x02);

  BLESecurity *pSecurity = new BLESecurity();
//  pSecurity->setKeySize();
  pSecurity->setAuthenticationMode(ESP_LE_AUTH_BOND);

  const uint8_t report[] = {
      USAGE_PAGE(1), 0x01, // Generic Desktop Ctrls
      USAGE(1), 0x06,      // Keyboard
      COLLECTION(1), 0x01, // Application
      REPORT_ID(1), 0x01,  //   Report ID (1)
      USAGE_PAGE(1), 0x07, //   Kbrd/Keypad
      USAGE_MINIMUM(1), 0xE0,
      USAGE_MAXIMUM(1), 0xE7,
      LOGICAL_MINIMUM(1), 0x00,
      LOGICAL_MAXIMUM(1), 0x01,
      REPORT_SIZE(1), 0x01, //   1 byte (Modifier)
      REPORT_COUNT(1), 0x08,
      HIDINPUT(1), 0x02,     //   Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position
      REPORT_COUNT(1), 0x01, //   1 byte (Reserved)
      REPORT_SIZE(1), 0x08,
      HIDINPUT(1), 0x01,     //   Const,Array,Abs,No Wrap,Linear,Preferred State,No Null Position
      REPORT_COUNT(1), 0x06, //   6 bytes (Keys)
      REPORT_SIZE(1), 0x08,
      LOGICAL_MINIMUM(1), 0x00,
      LOGICAL_MAXIMUM(1), 0x65, //   101 keys
      USAGE_MINIMUM(1), 0x00,
      USAGE_MAXIMUM(1), 0x65,
      HIDINPUT(1), 0x00,     //   Data,Array,Abs,No Wrap,Linear,Preferred State,No Null Position
      REPORT_COUNT(1), 0x05, //   5 bits (Num lock, Caps lock, Scroll lock, Compose, Kana)
      REPORT_SIZE(1), 0x01,
      USAGE_PAGE(1), 0x08,    //   LEDs
      USAGE_MINIMUM(1), 0x01, //   Num Lock
      USAGE_MAXIMUM(1), 0x05, //   Kana
      HIDOUTPUT(1), 0x02,     //   Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position,Non-volatile
      REPORT_COUNT(1), 0x01,  //   3 bits (Padding)
      REPORT_SIZE(1), 0x03,
      HIDOUTPUT(1), 0x01, //   Const,Array,Abs,No Wrap,Linear,Preferred State,No Null Position,Non-volatile
      END_COLLECTION(0)};

  hid->reportMap((uint8_t *)report, sizeof(report));
  hid->startServices();

  BLEService *pServiceUART = pServer->createService(SERVICE_UART_UUID);
  pTxCharacteristic = pServiceUART->createCharacteristic(CHARACTERISTIC_UUID_TX, BLECharacteristic::PROPERTY_NOTIFY);
  // Create a BLE Descriptor : Client Characteristic Configuration (for indications/notifications)
  pTxCharacteristic->addDescriptor(new BLE2902());
  pRxCharacteristic = pServiceUART->createCharacteristic(CHARACTERISTIC_UUID_RX, BLECharacteristic::PROPERTY_WRITE);
  pRxCharacteristic->setCallbacks(new MyOutputCallbacks());
  
  pServiceUART->start();

  BLEAdvertising *pAdvertising = pServer->getAdvertising();
  pAdvertising->setAppearance(HID_GAMEPAD);
  pAdvertising->addServiceUUID(hid->hidService()->getUUID());
  pAdvertising->start();
  hid->setBatteryLevel(100);

  ESP_LOGD(LOG_TAG, "Advertising started!");
  delay(portMAX_DELAY);
  
};

void initGamePad(const char* left, const char* right, const char* up, const char* down,
                 const char* A, const char* B, const char* start, const char* select) {
                   
  keyControls[0] = left;
  keyControls[1] = right;
  keyControls[2] = up;
  keyControls[3] = down;
  keyControls[4] = A;
  keyControls[5] = B;
  keyControls[6] = start;
  keyControls[7] = select;

  Serial.begin(115200);
  Serial.println("Starting BLE work!");

  xTaskCreate(taskServer, "server", 20000, NULL, 5, NULL);
}

void press(Controls direction) {
  if(connected){

    const char* hello = keyControls[(int)direction];

    while(*hello){
      KEYMAP map = keymap_fr[(uint8_t)*hello];
      uint8_t msg[] = {map.modifier, 0x0, map.usage, 0x0, 0x0, 0x0, 0x0, 0x0};
      input->setValue(msg,sizeof(msg));
      input->notify();
      hello++;
    }
  }
}

void release() {
  if (connected) {
    uint8_t msg1[] = {0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0};
    input->setValue(msg1,sizeof(msg1));
    input->notify();
  }
}

void pressThree(Controls first, Controls second, Controls third) {
  if(connected){

    const char* firstChar = keyControls[(int)first];
    const char* secondChar = keyControls[(int)second];
    const char* thirdChar = keyControls[(int)third];

    KEYMAP firstMap = keymap_fr[(uint8_t)*firstChar];
    KEYMAP secondMap = keymap_fr[(uint8_t)*secondChar];
    KEYMAP thirdMap = keymap_fr[(uint8_t)*thirdChar];

    uint8_t msg[] = {firstMap.modifier, 0x0, firstMap.usage, secondMap.usage, thirdMap.usage, 0x0, 0x0, 0x0};
    input->setValue(msg,sizeof(msg));
    input->notify();
  }
}

void sendTrame(uint8_t * chars) {
  if(connected){
    KEYMAP firstMap = keymap_fr[chars[0]];
    KEYMAP secondMap = keymap_fr[chars[1]];
    KEYMAP thirdMap = keymap_fr[chars[2]];
    uint8_t msg[] = {0x0, 0x0, firstMap.usage, secondMap.usage, thirdMap.usage, 0x0, 0x0, 0x0};
    input->setValue(msg,sizeof(msg));
    input->notify();
  }
}

void pressForSeconds(Controls key, float seconds){
  unsigned long now = millis();
  unsigned long until = now + seconds*1000;
  //unsigned long numberOfPress = 0;
  while(now < until) {
    press(key);
    now = millis();
    //numberOfPress ++;
  }
  //Serial.println(numberOfPress);
}