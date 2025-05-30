#include <LiquidCrystal_I2C.h>
#include <Wire.h>

#define SDA_GPIO_PIN 21
#define SCL_GPIO_PIN 22

#define NUM_COLS 20
#define NUM_ROWS 4
#define I2C_ADDR 0x27

LiquidCrystal_I2C lcd(I2C_ADDR, NUM_COLS, NUM_ROWS);

void setup() {
  Wire.begin(SDA_GPIO_PIN, SCL_GPIO_PIN);
  Serial.begin(115200);

  lcd.init();
  lcd.backlight();
  lcd.clear();

  Serial.println("\nType something and press Enter:\n");
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(input);

    Serial.print("Displayed on LCD: ");
    Serial.println(input);
  }
}
