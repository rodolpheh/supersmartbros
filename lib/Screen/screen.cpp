#include <Arduino.h>
#include <screen.h>

void init(){
    if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3C for 128x32
    for (;;);
    }
      display.clearDisplay();
}


void update_values(int *values) {
  display.clearDisplay();
  set_header("Super Mario");
  draw_heart();
  char val_1[20];
  char val_2[20];
  sprintf(val_1, "x%d", values[0]);
  sprintf(val_2, "x%d", values[1]);
  print_string(val_1, 40, 15);
  print_string(val_2, 95, 15);
  draw_coin();
  display.display();
}


void draw_heart() {
  int pos_x = (SCREEN_WIDTH / 6) * 1;
  const int heart_height = 20;
  const int heart_width = 20;
  const unsigned char heart [] PROGMEM = {
    // 'heart, 20x20px
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x0f, 0x9f, 0x00, 0x1f, 0xff, 0x80, 0x1f, 0xff,
    0x80, 0x1f, 0xff, 0x80, 0x1f, 0xff, 0x80, 0x0f, 0xff, 0x00,
    0x0f, 0xff, 0x00, 0x07, 0xfe, 0x00, 0x03, 0xfc, 0x00, 0x01,
    0xf8, 0x00, 0x00, 0xf0, 0x00, 0x00, 0x60, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
  };
  display.drawBitmap(pos_x, 8, heart, heart_width, heart_height, 1);
  display.display();
}

void draw_coin() {
  int pos_x = (SCREEN_WIDTH / 6) * 3.5;
  const int coin_height = 15;
  const int coin_width = 20;

  const unsigned char coin [] PROGMEM = {
    // '204-2044694_8-bit-mario-coin-super-mario-bros-3, 20x15px
    0x00, 0x00, 0x00, 0x01, 0xe0, 0x00, 0x0f, 0xfc, 0x00, 0x1f, 0xe7, 0x00, 0x1f, 0xe7, 0x00, 0x7f,
    0xe7, 0x80, 0x7f, 0xe7, 0x80, 0x7f, 0xe7, 0x80, 0x7f, 0xe7, 0x80, 0x7f, 0xe7, 0x80, 0x1f, 0xe7,
    0x00, 0x1e, 0x07, 0x00, 0x0f, 0xfc, 0x00, 0x01, 0xe0, 0x00, 0x00, 0x00, 0x00
  };
  display.drawBitmap(pos_x, 10, coin, coin_width, coin_height, 1);
  display.display();
}


void set_header(char *str) {
  int x = (SCREEN_WIDTH - strlen(str) * 4) / 2;
  print_string(str, x, 0);
}

void print_string(char* str, int x, int y) {
  display.setTextSize(1);      // Normal 1:1 pixel scale
  display.setTextColor(WHITE); // Draw white text
  display.setCursor(x, y);     // Start at top-left corner
  display.cp437(true);         // Use full 256 char 'Code Page 437' font
  for (int i = 0; i < strlen(str); i++) {
    display.write(str[i]);
  }
  display.display();
}
