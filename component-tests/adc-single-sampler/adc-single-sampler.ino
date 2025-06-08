// ESP-side

#include "BluetoothSerial.h"
BluetoothSerial SerialBT;

#define MIC_PIN 35
#define BT_DEVICE_NAME "ESP32SPP"

void setup() {
  Serial.begin(115200);
  Serial.println("Setting up...");
  delay(1000);

  if (SerialBT.begin(BT_DEVICE_NAME, false)) {
    Serial.println("Bluetooth started.");
    SerialBT.enableSSP();
  } else {
    Serial.println("Bluetooth failed to start");
  }

  if (SerialBT.isReady()) {
    Serial.println("Bluetooth is ready.");
  } else {
    Serial.println("Bluetooth not ready.");
  }

  analogReadResolution(12);        // 12-bit ADC resolution (0-4095)
  analogSetAttenuation(ADC_11db);  // Allow 0-2.45V signal (for ESP32 chip.
                                   // May differ for other boards)
}

void loop() {
  int sample = analogRead(MIC_PIN);
  uint8_t high_byte = (sample >> 8) & 0xFF;
  uint8_t low_byte = sample & 0xFF;

  Serial.printf("Sending: %d = [%02X %02X]\n", sample, high_byte, low_byte);
  SerialBT.write(high_byte);
  SerialBT.write(low_byte);

  // A target sampling rate f requires
  // a delay of T = 1/f seconds between samples.
  // For 8 kHz: T = 1/8000 = 0.000125 seconds = 125 us
  delayMicroseconds(125);

  // NOTE! The sample rate here isn’t accurate, because the delay time does
  // not account for the time it took to execute analogRead() and anything else.
}
