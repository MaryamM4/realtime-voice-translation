#include <LiquidCrystal_I2C.h>
#include <Wire.h>

#include <vector>

#define SCROLL_DELAY_MS 650

#define SDA_GPIO_PIN 21
#define SCL_GPIO_PIN 22

#define NUM_COLS 20
#define NUM_ROWS 4
#define I2C_ADDR 0x27

LiquidCrystal_I2C lcd(I2C_ADDR, NUM_COLS, NUM_ROWS);
String lcdBuffer[NUM_ROWS];

std::vector<String> wrapText(const String& text);
void scrollAndAddLine(const String& newLine);
void refreshLCD();

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
    input.trim();

    // Split input into wrapped lines
    auto wrappedLines = wrapText(input);

    for (String& line : wrappedLines) {
      scrollAndAddLine(line);
      refreshLCD();
      delay(SCROLL_DELAY_MS);  // Give time for user to read.
    }

    Serial.print("Displayed on LCD:\n");
    for (int i = 0; i < NUM_ROWS; i++) {
      Serial.println(lcdBuffer[i]);
    }
  }
}

// Wraps text into lines with word boundary respecting screen width
std::vector<String> wrapText(const String& text) {
  std::vector<String> lines;
  int start = 0;
  int end;
  int space_idx;

  while (start < text.length()) {
    end = start + NUM_COLS;

    if (end >= text.length()) {
      lines.push_back(text.substring(start));
      break;
    }

    space_idx =
        text.lastIndexOf(' ', end);  // Break on last space within screen width.
    if (space_idx <= start) {
      space_idx = end;
    }  // If the word is too long, force it.

    lines.push_back(text.substring(start, space_idx));
    start = space_idx;

    // Skip any spaces at the start of the next line
    while (start < text.length() && text[start] == ' ') {
      start++;
    }
  }

  return lines;
}

// Scrolls lines up and appends a new one at the bottom
void scrollAndAddLine(const String& newLine) {
  for (int i = 0; i < NUM_ROWS - 1; i++) {
    lcdBuffer[i] = lcdBuffer[i + 1];
  }
  lcdBuffer[NUM_ROWS - 1] = newLine;
}

// Writes entire buffer to the LCD
void refreshLCD() {
  lcd.clear();
  for (int i = 0; i < NUM_ROWS; i++) {
    lcd.setCursor(0, i);
    lcd.print(lcdBuffer[i]);
  }
}