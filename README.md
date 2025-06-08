# Realtime Voice Translation

A microcontroller-based voice translation system that captures spoken input via a microphone, 
streams audio to a host PC for real-time speech-to-text transcription and translation, 
and displays the translated text on an LCD screen. 


## Components
- **DOIT ESP32 DEVKIT V1 Microcontroller**
  - Captures audio via 12-bit ADC at 40 kHz using I2S + DMA
    
- **MAX9814 microphone**
  
- **Bluetooth Classic using Serial Port Profile (SPP)** for wireless communication
  - Streams audio samples from ESP32 to PC, and sends translated text back from PC to ESP32
  
- **Python-based PC client**
  - Reconstructs streamed audio in real time, processes and translates it, and sends UTF-8 results to ESP32.

- **I2C 16x2 LCD Display**
