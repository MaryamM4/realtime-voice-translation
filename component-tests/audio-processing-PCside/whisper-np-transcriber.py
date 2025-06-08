import array
import threading
import pyaudio
import serial  # pip3 install pyserial
import time
import whisper  # pip install -U openai-whisper
import numpy as np
from scipy.signal import resample, butter, filtfilt
from scipy.io.wavfile import write as wavwrite
import matplotlib.pyplot as plt  # pip install matplotlib

# Serial settings need to match the virtual serial COM port the PC creates
SERIAL_PORT = "COM4"  # ESP32 (outgoing) -> PC
BAUD_RATE = 115200
PORT_TIMEOUT = 1

# PyAudio settings
SAMPLE_RATE = 12000  # Hz = samples/second. Must match ESP32’s I2D audio output config.
CHUNK_SIZE = 512  # Small = faster updates, more CPU
FORMAT = pyaudio.paInt16  # 16-bit signed integers
NUM_CHANNELS = 1  # 1-> mono, 2-> stereo

# Whisper model
model = whisper.load_model("small")
BUFFER_DURATION = 8  # seconds
TRANSCRIBE_THRESHOLD = SAMPLE_RATE * BUFFER_DURATION * 2  # 2 bytes/sample

# Shared buffer and lock
accumulated_audio = bytearray()
buffer_lock = threading.Lock()
running = True


# Usage: audio_np = highpass_filter(audio_np, fs=SAMPLE_RATE)
def highpass_filter(data, cutoff=100.0, fs=12000, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype="high", analog=False)
    return filtfilt(b, a, data)


def transcription_thread():
    global accumulated_audio, running

    while running:
        time.sleep(1.0)  # Poll roughly every second

        with buffer_lock:
            if len(accumulated_audio) >= TRANSCRIBE_THRESHOLD:
                # Extract and reset buffer
                audio_data = accumulated_audio[:TRANSCRIBE_THRESHOLD]
                accumulated_audio = accumulated_audio[TRANSCRIBE_THRESHOLD:]
            else:
                continue

        # Convert to float32 [-1, 1]
        audio_np = np.frombuffer(audio_data, np.int16).astype(np.float32) / 32768.0

        # === Preprocessing ===

        # 1. Remove DC offset
        audio_np -= np.mean(audio_np)

        # 2. Normalize to [-1, 1] by max abs value (avoid dividing by zero)
        peak = np.max(np.abs(audio_np))
        if peak > 0:
            audio_np /= peak

        # 3. Optional soft clipping (clamps to avoid harsh clipping noise)
        audio_np = np.clip(audio_np, -1.0, 1.0)

        # 4. Resample to 16 kHz for Whisper
        num_target_samples = int(len(audio_np) * 16000 / SAMPLE_RATE)
        resampled = resample(audio_np, num_target_samples)

        # --- Debug info below ---

        # Save audio chunk to file
        wavwrite("debug_chunk.wav", 16000, (resampled * 32767).astype(np.int16))
        print("Saved debug_chunk.wav")

        # Print min/max to check volume or silence
        print(
            f"Audio range after normalization: {audio_np.min():.3f} to {audio_np.max():.3f}"
        )

        # Plot waveform (first 1000 samples)
        plt.figure(figsize=(8, 2))
        plt.plot(audio_np[:1000])
        plt.title("Waveform Preview (First 1000 Samples, Normalized)")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("debug_waveform.png")
        plt.close()
        print("Saved debug_waveform.png")

        # Run Whisper transcription
        result = model.transcribe(resampled, language="ar", verbose=True)
        print(f"[{result['language']}] {result['text'].strip()}")


def main():
    global accumulated_audio, running

    ser = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=PORT_TIMEOUT)
    time.sleep(2)  # Wait for ESP32 handshake
    ser.flushInput()
    print("Connected.")

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=NUM_CHANNELS, rate=SAMPLE_RATE, output=True)

    thread = threading.Thread(target=transcription_thread, daemon=True)
    thread.start()
    print("Starting...\n")

    try:
        while True:
            buffer = ser.read(CHUNK_SIZE)  # Simpler, avoids partial reads

            if len(buffer) > 0:
                # Ensure samples are not incomplete (each should be 2 bytes (int16))
                if len(buffer) % 2 != 0:
                    buffer = buffer[:-1]  # Drop extra byte

                # Convert to signed 16-bit PCM
                data = array.array("h", buffer)

                # Play audio
                stream.write(data.tobytes())

                # Store for transcription
                with buffer_lock:
                    accumulated_audio += buffer

    except KeyboardInterrupt:
        print("User terminated program.")

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        ser.close()
        running = False
        thread.join()


if __name__ == "__main__":
    main()
