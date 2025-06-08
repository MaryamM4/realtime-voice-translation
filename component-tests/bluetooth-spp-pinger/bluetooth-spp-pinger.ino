// Basic ESP-side ping program to test Bleutooth SPP.

/*
TO VIEW FROM THE PC-END:

1. Settings > Bluetooth > add device

2. Find virtual port number:
   Control Panel > Devices & Printers > (Right-click ESP32 Device)
   -> Properties > Hardware
   Look for: Standard Serial over Bluetooth link (COM#)

3. Use PuTTY to check the Bluetooth stream from the ESP32.
  - Session type: Serial
  - Serial line: COM#
  - Speed: 115200
*/

#include "BluetoothSerial.h"
BluetoothSerial SerialBT;

#define BT_DEVICE_NAME "ESP32SPP"
bool lastConnected = false;

void setup() {
  Serial.begin(115200);
  delay(2500);

  // SerialBT.enableSSP();  // Enable secure pairing

  // True->master, False->server mode
  if (SerialBT.begin(BT_DEVICE_NAME, false)) {
    Serial.println("Bluetooth started as ESP32SPP");

  } else {
    Serial.println("Bluetooth failed to start");
  }

  Serial.println(SerialBT.isReady() ? "Bluetooth is ready.\n"
                                    : "Bluetooth not ready.\n");
}

void loop() {
  // Even if not connected yet, Bluetooth Classic SPP devices may
  // need to transmit data for PC to detect them.
  SerialBT.println("Hello from ESP32!");

  bool connected = SerialBT.hasClient() || SerialBT.connected();

  if (connected && !lastConnected) {
    Serial.println("Client connected.");

  } else if (!connected && lastConnected) {
    Serial.println("Client disconnected.");
  }

  lastConnected = connected;
  delay(1000);
}
