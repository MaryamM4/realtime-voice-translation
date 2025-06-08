import array
import pyaudio
import serial  # pip3 install pyserial
import time

#  Serial settings need to match the virtual serial COM port the PC creates
SERIAL_PORT = "COM4"  # ESP32 (outgoing) -> PC
BAUD_RATE = 115200
# Timeout is up to you. Limiting how many sec(s) blocking read/write operations take
PORT_TIMEOUT = 1


# PyAudio settings
SAMPLE_RATE = 12000  # Hz = samples/second. Must match ESP32’s I2D audio output config.
CHUNK_SIZE = 512  # Instead of continuous data, it’s store in buffer (512/1024 common sizes). Smaller is faster for real-time applications but means more reads
FORMAT = pyaudio.paInt16  # 16-bit signed integers
NUM_CHANNELS = 1  # 1-> mono, 2-> stereo (left & right)


def main():
    # Open the virtual port
    ser = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=PORT_TIMEOUT)
    time.sleep(2)  # Wait for ESP32 to init connection
    ser.flushInput()  # Discard noise

    # Setup PyAudio as output stream to allow playback
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=NUM_CHANNELS, rate=SAMPLE_RATE, output=True)

    try:
        while True:  # PLAYBACK LOOP:
            buffer = bytearray()

            while len(buffer) < CHUNK_SIZE:  # (1) Read a chunk data from serial port
                if ser.in_waiting:
                    bytes_to_read = min(ser.in_waiting, CHUNK_SIZE - len(buffer))
                    buffer += ser.read(bytes_to_read)

            if len(buffer) > 0:
                # Read as signed 16-bit PCM
                data = array.array("h", buffer)
                stream.write(data.tobytes())  # (2) Play the audio

    except KeyboardInterrupt:
        print("User terminated program.")

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        ser.close()


if __name__ == "__main__":
    main()
