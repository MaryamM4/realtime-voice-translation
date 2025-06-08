import array
import pyaudio
import serial
import time
import wave

# Serial settings
SERIAL_PORT = "COM4"
BAUD_RATE = 115200
PORT_TIMEOUT = 1

# Audio settings
SAMPLE_RATE = 12000
CHUNK_SIZE = 512
FORMAT = pyaudio.paInt16
NUM_CHANNELS = 1
WAV_FILENAME = "esp_recorded_audio.wav"


def main():
    ser = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=PORT_TIMEOUT)
    time.sleep(2)
    ser.flushInput()

    p = pyaudio.PyAudio()
    all_audio_data = bytearray()

    try:
        print("Recording... Press Ctrl+C to stop.")
        while True:
            buffer = bytearray()
            while len(buffer) < CHUNK_SIZE:
                if ser.in_waiting:
                    bytes_to_read = min(ser.in_waiting, CHUNK_SIZE - len(buffer))
                    buffer += ser.read(bytes_to_read)

            if buffer:
                all_audio_data += buffer

    except KeyboardInterrupt:
        print("\nRecording stopped. Saving to", WAV_FILENAME)

        with wave.open(WAV_FILENAME, "wb") as wf:
            wf.setnchannels(NUM_CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(all_audio_data)

    finally:
        p.terminate()
        ser.close()


if __name__ == "__main__":
    main()
