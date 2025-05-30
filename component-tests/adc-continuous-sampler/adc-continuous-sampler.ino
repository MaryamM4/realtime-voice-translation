// ESP-side

#include <Arduino.h>

#include "BluetoothSerial.h"
#include "driver/adc.h"
#include "driver/i2s.h"

BluetoothSerial SerialBT;
#define BT_DEVICE_NAME "ESP32SPP"
#define MAX_CONNECTION_ATTEMPTS 10

#define I2S_SAMPLE_RATE 12000
#define I2S_DMA_BUF_LEN 512
#define I2S_DMA_BUF_COUNT 2
#define ADC_BUFFER_SIZE I2S_DMA_BUF_LEN

uint8_t adcBuffer[ADC_BUFFER_SIZE];

void adc_sampler(void *param);
static QueueHandle_t i2s_queue;

void setup() {
  Serial.begin(115200);

  // Bluetooth Setup
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
  Serial.print("\nBluetooth name: ");
  Serial.println(BT_DEVICE_NAME);

  Serial.println("Configuring ADC & setting up I2S...");

  // 12-bit resolution (0-4095)
  adc1_config_width(ADC_WIDTH_BIT_12);
  // Set attenuation to 11 dB (~0–2.45V)
  adc1_config_channel_atten(ADC1_CHANNEL_7, ADC_ATTEN_DB_11);
  pinMode(35, INPUT);
  // Required for I2S ADC mode
  adc_gpio_init(ADC_UNIT_1, (adc_channel_t)ADC1_CHANNEL_7);

  // I2S Setup
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

  // Start ADC reading task
  xTaskCreatePinnedToCore(adc_sampler, "ADC Reader", 4096, NULL, 1, NULL, 0);

  Serial.println("Setup complete.");
}

void loop() {
  if (!SerialBT.connected()) {
    Serial.println("[Bluetooth] Not connected.");
  }
  if (!SerialBT.hasClient()) {
    SerialBT.println("Ping from ESP32");
    delay(1000);
  }
}

void adc_sampler(void *param) {
  while (true) {
    size_t bytes_read = 0;
    esp_err_t result = i2s_read(I2S_NUM_0, (void *)adcBuffer, sizeof(adcBuffer),
                                &bytes_read, portMAX_DELAY);

    if (result == ESP_OK && bytes_read > 0 && SerialBT.hasClient()) {
      int sample_count = bytes_read / sizeof(int16_t);
      int16_t *samples = (int16_t *)adcBuffer;

      // i2s_read() returns 16-bit values where only the 12 most significant
      // bits are the audio data.
      for (int i = 0; i < sample_count; i++) {
        // So shift each sample back to 12-bit to remove irrelevant bits.
        samples[i] = samples[i] >> 4;

        // Audio streams use 8/16/24/32-bit samples, so center
        // and scale 12-bit ADC value to a signed 16-bit for transmission
        samples[i] = (samples[i] - 2048) << 4; 
      }

      Serial.print("Sending samples: ");
      for (int i = 0; i < min(sample_count, 10); i++) {
        Serial.print(samples[i]);
        Serial.print(i < min(sample_count, 10) - 1 ? ", " : "\n");
      }

      // This was for debugging, but is blocking and broke the program instead.
      // int raw = adc1_get_raw(ADC1_CHANNEL_7); // Blocking ADC read!
      // Serial.printf("Raw ADC reading: %d\n\n", raw);

      SerialBT.write((uint8_t *)samples, sample_count * sizeof(int16_t));
      vTaskDelay(10 / portTICK_PERIOD_MS);  // Slow down slightly to avoid
                                            // overwhelming Bluetooth

    } else {
      if (result != ESP_OK) {
        Serial.printf("I2S read failed with error: %d\n", result);

      } else if (!SerialBT.hasClient()) {
        Serial.println("[Bluetooth] No client.");

      } else if (!bytes_read > 0) {
        Serial.println("Buffer empty.");
      }

      vTaskDelay(20 / portTICK_PERIOD_MS);  // Yeild to other tasks
    }
  }
}
