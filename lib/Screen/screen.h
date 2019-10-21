#ifndef SCREENLIB_H_
#define SCREENLIB_H_
#include <SPI.h>
#include <Wire.h>
#include <time.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 32 // OLED display height, in pixels

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
#define OLED_RESET     4 // Reset pin # (or -1 if sharing Arduino reset pin)
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

#define NUMFLAKES     10 // Number of snowflakes in the animation example

 
void init(); // Clear and test the screen
void score(char* score); //Display score
void draw_heart(); // Draw heart BMP
void draw_coin(); // Draw coin BMP  
void set_header(char *str); // Set the header (yellow color)
void print_string(char* str, int x, int y); //Print a string on the screen (str,x, y)
int parseInt(char* chars);
int powInt(int x, int y);
void display_screen_2(char *world, char *life); // Screen when world change or you die
void display_screen_1(char *lifes, char *coins, char *val_score); // Screen in game
void draw_head(); // Draw mario head BMP


#endif