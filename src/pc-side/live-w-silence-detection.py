import array
import time
import serial
import numpy as np
import whisper
from scipy.signal import resample

# Serial config
SERIAL_PORT = "COM4"
BAUD_RATE = 115200
PORT_TIMEOUT = 1

# Audio config
INPUT_SAMPLE_RATE = 12000
TARGET_SAMPLE_RATE = 16000
FORMAT_WIDTH = 2  # bytes per sample for 16-bit audio
CHUNK_SIZE = 512  # bytes
MIN_DURATION_SEC = 1.5
MAX_DURATION_SEC = 6

MIN_SAMPLES = int(MIN_DURATION_SEC * INPUT_SAMPLE_RATE)
MAX_SAMPLES = int(MAX_DURATION_SEC * INPUT_SAMPLE_RATE)

# Silence detection confi
SILENCE_THRESHOLD = 0.02  # Normalized amplitude below which we consider it silent
SILENCE_DURATION_SEC = 0.8  # Stop recording if this much silence is detected
SILENCE_WINDOW_SIZE = int(SILENCE_DURATION_SEC * INPUT_SAMPLE_RATE)

# Whisper config
LANG = "ar"
MODEL_SIZE = "large-v3"


def decode_audio(buffer):
    audio_int16 = np.frombuffer(buffer, dtype=np.int16).astype(np.float32)
    audio_int16 /= 32768.0
    audio_int16 -= np.mean(audio_int16)
    peak = np.max(np.abs(audio_int16))
    if peak > 0:
        audio_int16 /= peak

    num_samples = int(len(audio_int16) * TARGET_SAMPLE_RATE / INPUT_SAMPLE_RATE)
    return resample(audio_int16, num_samples)


def is_silence(window, threshold=SILENCE_THRESHOLD):
    return np.max(np.abs(window)) < threshold


def main():
    print("Loading model... ")
    model = whisper.load_model(MODEL_SIZE)

    print("Opening serial port... ")
    ser = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=PORT_TIMEOUT)
    time.sleep(2)
    ser.flushInput()

    print("Starting.\n")

    try:
        print("Waiting for incoming audio...")

        while True:
            buffer = bytearray()
            audio_float_buffer = np.zeros(0, dtype=np.float32)

            print("\nListening...")

            while True:
                if ser.in_waiting:
                    chunk = ser.read(min(CHUNK_SIZE, ser.in_waiting))
                    buffer += chunk

                    # Decode & normalize latest chunk
                    new_samples = np.frombuffer(chunk, dtype=np.int16).astype(
                        np.float32
                    )
                    new_samples /= 32768.0
                    audio_float_buffer = np.concatenate(
                        (audio_float_buffer, new_samples)
                    )

                    # Stop if too much audio
                    if len(audio_float_buffer) > MAX_SAMPLES:
                        print("Reached max duration.")
                        break

                    # Stop if enough silence after minimum duration
                    if len(audio_float_buffer) > MIN_SAMPLES:
                        recent_window = audio_float_buffer[-SILENCE_WINDOW_SIZE:]
                        if len(recent_window) == SILENCE_WINDOW_SIZE and is_silence(
                            recent_window
                        ):
                            print("Silence detected.")
                            break
                else:
                    time.sleep(0.01)

            print(f"Captured {len(buffer)} bytes. Transcribing...")

            audio = decode_audio(buffer)
            result = model.transcribe(audio, language=LANG, task="translate")
            translated_text = result["text"].strip()
            print("\nTranslated:\n", translated_text)

            if translated_text:
                ser.write(translated_text.encode("utf-8") + b"\n")

    except KeyboardInterrupt:
        print("User stopped the program.")
    finally:
        ser.close()


if __name__ == "__main__":
    main()
