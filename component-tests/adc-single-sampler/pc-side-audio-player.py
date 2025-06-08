# This doesn't work for multiple potential reasons, such as
# - Sampling rate on ESP-end is too slow
# - Mismatched send/recieve rates

import serial
import pyaudio
import struct

# === Serial Setup ===
ser = serial.Serial("COM4", baudrate=115200)
print("Connected to serial")

# === PyAudio Setup ===
p = pyaudio.PyAudio()

stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=8000,  # Match the ESP32's sample rate. 8000 if 8kHz.
    output=True,
    frames_per_buffer=256,
)

try:
    while True:
        # Read two bytes
        raw = ser.read(2)
        if len(raw) < 2:
            continue

        high, low = raw[0], raw[1]
        sample = (high << 8) | low

        # Convert from unsigned 12-bit (0–4095) to signed 16-bit (-32768 to 32767)
        # Step 1: center around 0: (e.g., 0–4095 => -2048 to +2047)
        sample -= 2048

        # Step 2: scale to 16-bit
        sample = int(sample * 16)

        # Pack as signed 16-bit little-endian for PyAudio
        pcm_bytes = struct.pack("<h", sample)
        stream.write(pcm_bytes)

except KeyboardInterrupt:
    print("Stopping...")

finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    ser.close()
