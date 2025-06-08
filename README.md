# ESP32 Real-Time Translator (MVP)
**CSS427 Final Project – May 2025**
This project is a minimum viable prototype for a real-time translation device using an ESP32 microcontroller and a host PC. It captures spoken audio, transmits it over Bluetooth Serial (SPP), performs speech-to-translation on the PC, and displays the translated text on an LCD screen connected to the ESP32.

## Features
- Microphone audio sampling using ESP32's ADC + I2S + DMA
- Real-time audio transmission over Bluetooth SPP
- Speech-to-English translation using Whisper (large-v3) on the PC
- Translated text sent back and displayed on an I2C LCD

## Components
- DOIT ESP32 DEVKIT V1
- MAX9814 Microphone Amplifier Module
- 20x4 I2C LCD Display (with PCF8574 backpack)
- Host PC (Windows, with Python + PySerial + PyAudio + Whisper)
- Battery pack (used to power LCD backlight separately)

## Wiring
### MAX9814 to ESP32
- `VCC` → 3.3V  
- `GND` → GND  
- `OUT` → GPIO35 (ADC1_CH7)

### LCD to ESP32 & Battery
- `SDA` → GPIO21  
- `SCL` → GPIO22  
- `VCC` → Battery VCC  
- `GND` → Shared GND (ESP32 + Battery)

## PC Requirements
- Python 3.8+
- COM port set correctly in the script (check via Device Manager)

# Running the System
## ESP32
1. Connect microphone, LCD and battery
1. Flash the sketch using Arduino IDE (src/esp-side/esp-side.ino)

## PC
1. Run the python program (src/pc-side/prompted.py)
2. Press Enter to start/stop recording audio
3. Wait for the translation to appear on the LCD

# Note
- Audio is buffered between prompts; streaming is not yet real-time
- Translation is Arabic → English only
- LCD overflow is handled with simple word-wrapped scrolling
- Ensure the LCD backlight has external power to avoid brownouts
