import time
import serial
import numpy as np
import whisper
import threading
from scipy.signal import resample

# Serial config
SERIAL_PORT = "COM4"
BAUD_RATE = 115200
PORT_TIMEOUT = 1

# Audio config
INPUT_SAMPLE_RATE = 12000
TARGET_SAMPLE_RATE = 16000
FORMAT_WIDTH = 2
CHUNK_SIZE = 512
MAX_DURATION_SEC = 10
MAX_SAMPLES = int(MAX_DURATION_SEC * INPUT_SAMPLE_RATE)

# Whisper config
LANG = "ar"
MODEL_SIZE = "large-v3"


stop_recording = False


def decode_audio(buffer):
    audio_int16 = np.frombuffer(buffer, dtype=np.int16).astype(np.float32)
    audio_int16 /= 32768.0
    audio_int16 -= np.mean(audio_int16)
    peak = np.max(np.abs(audio_int16))
    if peak > 0:
        audio_int16 /= peak

    num_samples = int(len(audio_int16) * TARGET_SAMPLE_RATE / INPUT_SAMPLE_RATE)
    return resample(audio_int16, num_samples)


def wait_for_enter():
    global stop_recording
    input()  # Block until Enter is pressed
    stop_recording = True


def main():
    global stop_recording

    print("Loading Whisper model...")
    model = whisper.load_model(MODEL_SIZE)

    print("Opening serial port...")
    ser = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=PORT_TIMEOUT)
    time.sleep(2)
    ser.flushInput()

    print("\nReady. You’ll be prompted to press Enter to start and stop recording.\n")

    try:
        while True:
            input("Press Enter to START recording...")

            stop_recording = False
            buffer = bytearray()

            # Launch background thread to wait for user to stop
            threading.Thread(target=wait_for_enter, daemon=True).start()

            print("Recording... Press Enter again to STOP.")

            while not stop_recording:
                if ser.in_waiting:
                    chunk = ser.read(min(CHUNK_SIZE, ser.in_waiting))
                    buffer += chunk

                    if len(buffer) > MAX_SAMPLES * FORMAT_WIDTH:
                        print("Reached max duration.")
                        break

                time.sleep(0.01)

            print(f"\nCaptured {len(buffer)} bytes. Transcribing...")

            audio = decode_audio(buffer)
            result = model.transcribe(audio, language=LANG, task="translate")
            translated_text = result["text"].strip()
            print("\nTranslated:\n", translated_text)

            if translated_text:
                ser.write(translated_text.encode("utf-8") + b"\n")

            print("\n--- Done ---\n")

    except KeyboardInterrupt:
        print("User interrupted.")
    finally:
        ser.close()


if __name__ == "__main__":
    main()
