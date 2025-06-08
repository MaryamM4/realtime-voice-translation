#include <Arduino.h>
#include <BluetoothSerial.h>
#include <LiquidCrystal_I2C.h>
#include <Wire.h>

#include <vector>

#include "driver/adc.h"
#include "driver/i2s.h"

// ----- CONFIG -----
#define BT_DEVICE_NAME "ESP32SPP"
#define MAX_CONNECTION_ATTEMPTS 10

#define I2S_SAMPLE_RATE 12000
#define I2S_DMA_BUF_LEN 512
#define I2S_DMA_BUF_COUNT 2
#define ADC_BUFFER_SIZE I2S_DMA_BUF_LEN

#define SDA_GPIO_PIN 21
#define SCL_GPIO_PIN 22

#define NUM_COLS 20
#define NUM_ROWS 4
#define I2C_ADDR 0x27
#define SCROLL_DELAY_MS 650

BluetoothSerial SerialBT;
LiquidCrystal_I2C lcd(I2C_ADDR, NUM_COLS, NUM_ROWS);
String lcdBuffer[NUM_ROWS];

uint8_t adcBuffer[ADC_BUFFER_SIZE];
static QueueHandle_t i2s_queue;

void adc_sampler(void *param);
std::vector<String> wrapText(const String &text);
void scrollAndAddLine(const String &newLine);
void refreshLCD();
void displayRecievedText();

void setup() {
  Serial.begin(115200);
  Serial.println("\nBooting...");

  // Bluetooth setup
  int attempt_count = 0;
  while (!SerialBT.begin(BT_DEVICE_NAME, false) &&
         attempt_count < MAX_CONNECTION_ATTEMPTS) {
    Serial.printf("Retrying Bluetooth (%d)...\n", ++attempt_count);
    delay(2000);
  }

  if (attempt_count >= MAX_CONNECTION_ATTEMPTS) {
    Serial.println("Bluetooth failed. Restarting...");
    delay(1000);
    esp_restart();
  }
  Serial.print("Bluetooth has been setup (Bluetooth name: ");
  Serial.print(BT_DEVICE_NAME);
  Serial.println("). ");

  // ADC & I2S Setup
  Serial.println("Configuring ADC & setting up I2S...");
  adc1_config_width(ADC_WIDTH_BIT_12);  // 12-bit resolution (0-4095)
  adc1_config_channel_atten(
      ADC1_CHANNEL_7, ADC_ATTEN_DB_11);  //  Sets attenuation to 11 dB (~0–3.3V)
  pinMode(35, INPUT);
  adc_gpio_init(ADC_UNIT_1,
                (adc_channel_t)ADC1_CHANNEL_7);  // Required for I2S ADC mode

  i2s_config_t i2s_config = {
      .mode =
          (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX | I2S_MODE_ADC_BUILT_IN),
      .sample_rate = I2S_SAMPLE_RATE,
      .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
      .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
      .communication_format = I2S_COMM_FORMAT_I2S_LSB,
      .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
      .dma_buf_count = I2S_DMA_BUF_COUNT,
      .dma_buf_len = I2S_DMA_BUF_LEN,
      .use_apll = false,
      .tx_desc_auto_clear = false,
      .fixed_mclk = 0};

  i2s_driver_install(I2S_NUM_0, &i2s_config, 4, &i2s_queue);
  i2s_set_adc_mode(ADC_UNIT_1, ADC1_CHANNEL_7);  // GPIO35 = ADC1_CH7
  i2s_adc_enable(I2S_NUM_0);

  Serial.println("ADC and I2S have been setup.");

  // LCD Setup
  Wire.begin(SDA_GPIO_PIN, SCL_GPIO_PIN);
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);

  lcd.print("Ready.");
  Serial.println("LCD has been setup.");

  // Start ADC task.
  Serial.println("Starting ADC task...");
  xTaskCreatePinnedToCore(adc_sampler, "ADC Reader", 4096, NULL, 1, NULL, 0);

  Serial.println("Setup complete!\n");
}

void loop() {
  if (!SerialBT.connected()) {
    Serial.println("[Bluetooth] Not connected.");
    delay(2000);
  }
  if (!SerialBT.hasClient()) {
    SerialBT.println("Ping from ESP32");
    delay(1000);
    return;
  }

  displayRecievedText();  // Continuously check for incoming text from PC
}

// Audio sampleing & transmission
// @TODO: Logic should be seperated
void adc_sampler(void *param) {
  while (true) {
    size_t bytes_read = 0;
    esp_err_t result = i2s_read(I2S_NUM_0, (void *)adcBuffer, sizeof(adcBuffer),
                                &bytes_read, portMAX_DELAY);

    if (result == ESP_OK && bytes_read > 0 && SerialBT.hasClient()) {
      int sample_count = bytes_read / sizeof(int16_t);
      int16_t *samples = (int16_t *)adcBuffer;

      for (int i = 0; i < sample_count; i++) {
        samples[i] = (samples[i] >> 4);         // 12-bit
        samples[i] = (samples[i] - 2048) << 4;  // Signed 16-bit
      }

      // Serial.println("Sending samples. ");
      SerialBT.write((uint8_t *)samples, sample_count * sizeof(int16_t));
      vTaskDelay(10 / portTICK_PERIOD_MS);  // Slow down slightly to avoid
                                            // overwhelming Bluetooth

    } else {
      if (result != ESP_OK) {
        Serial.printf("I2S read failed with error: %d\n", result);
      } else if (!SerialBT.hasClient()) {
        Serial.println("[Bluetooth] No client.");
        delay(1000);
      } else if (!bytes_read > 0) {
        Serial.println("Buffer empty.");
      }

      vTaskDelay(20 / portTICK_PERIOD_MS);  // Yeild to other tasks
    }
  }
}

// Recieve text over bluetooth and display on LCD
// @TODO: Logic should be seperated
void displayRecievedText() {
  static String buffer;

  while (SerialBT.available()) {
    char c = SerialBT.read();

    if (c == '\n') {
      buffer.trim();

      if (buffer.length() > 0) {
        Serial.println("[Received] " + buffer);

        auto lines = wrapText(buffer);
        for (String &line : lines) {
          scrollAndAddLine(line);
          refreshLCD();
          delay(SCROLL_DELAY_MS);
        }
      }
      buffer = "";  // Clear buffer after newline

    } else {
      buffer += c;
    }
  }
}

// LCD helper functions

std::vector<String> wrapText(const String &text) {
  std::vector<String> lines;
  int start = 0;

  while (start < text.length()) {
    int end = start + NUM_COLS;
    if (end >= text.length()) {
      lines.push_back(text.substring(start));
      break;
    }

    int spaceIndex = text.lastIndexOf(' ', end);
    if (spaceIndex <= start) spaceIndex = end;
    lines.push_back(text.substring(start, spaceIndex));
    start = spaceIndex;
    while (start < text.length() && text[start] == ' ') start++;
  }

  return lines;
}

void scrollAndAddLine(const String &newLine) {
  for (int i = 0; i < NUM_ROWS - 1; i++) {
    lcdBuffer[i] = lcdBuffer[i + 1];
  }
  lcdBuffer[NUM_ROWS - 1] = newLine;
}

void refreshLCD() {
  lcd.clear();
  for (int i = 0; i < NUM_ROWS; i++) {
    lcd.setCursor(0, i);
    lcd.print(lcdBuffer[i]);
  }
}
