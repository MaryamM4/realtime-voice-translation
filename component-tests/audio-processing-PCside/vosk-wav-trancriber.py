"""
Failed to create model.
"""

# pip install: vosk, soundfile
from vosk import Model, KaldiRecognizer
import soundfile as sf
import json
import numpy as np
import sys


# Load model
try:
    model = Model("vosk-model-ar-mgb2-0.4")
    print("Model loaded successfully!")

except Exception as e:
    print(f"\nFailed to load model: {e}\n")
    sys.exit(1)

# Load audio
audio, sr = sf.read("normalized_resampled.wav")
assert sr == 16000, "Vosk requires 16kHz audio"

# Initialize recognizer
rec = KaldiRecognizer(model, sr)

# Convert audio to 16-bit PCM bytes
int16_audio = (audio * 32767).astype(np.int16).tobytes()

# Run recognition
if rec.AcceptWaveform(int16_audio):
    result = rec.Result()
    print(json.loads(result)["text"])
else:
    print("No valid transcription.")
