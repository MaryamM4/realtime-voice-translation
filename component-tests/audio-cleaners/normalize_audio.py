import numpy as np
import whisper
import soundfile as sf
from scipy.io import wavfile
from scipy.signal import resample, wiener
from my_local_paths import ESP_WAV_PATH, ESP_NORM_PATH

# Load WAV file
sr, data = wavfile.read(ESP_WAV_PATH)  # Assumes int16
print(f"Original SR: {sr}, dtype: {data.dtype}")

# Normalize to float
if data.dtype == np.int16:
    audio = data.astype(np.float32) / 32768.0
else:
    raise ValueError("Expected int16 WAV")

# Remove DC offset
audio -= np.mean(audio)

# Apply Wiener noise reduction
# audio = wiener(audio)         # Audio became grainy and noisy

# Normalize peak amplitude
peak = np.max(np.abs(audio))
if peak > 0:
    audio /= peak

# Resample to 16000 Hz
target_sr = 16000
if sr != target_sr:
    num_samples = int(len(audio) * target_sr / sr)
    audio = resample(audio, num_samples)

# Save as proper float32 WAV
sf.write(ESP_NORM_PATH, audio, target_sr, subtype="PCM_16")
print("\nSaved to:", ESP_NORM_PATH, "\n")
