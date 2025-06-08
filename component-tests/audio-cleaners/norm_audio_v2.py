# Doesn't work!

import numpy as np
import librosa
import noisereduce as nr
import soundfile as sf
from my_local_paths import ESP_WAV_PATH, ESP_NORM_PATH

# pip install librosa noisereduce soundfile


# Load audio with librosa (auto-converts to float32 and mono)
audio, sr = librosa.load(ESP_WAV_PATH, sr=None, mono=True)
print(f"Original SR: {sr}, shape: {audio.shape}")

# Remove DC offset
audio = audio - np.mean(audio)

# Apply noise reduction
audio_denoised = nr.reduce_noise(y=audio, sr=sr, prop_decrease=1.0)

# Resample to 16000 Hz
target_sr = 16000
if sr != target_sr:
    audio_denoised = librosa.resample(audio_denoised, orig_sr=sr, target_sr=target_sr)

# Normalize only if needed (optional)
peak = np.max(np.abs(audio_denoised))
if peak > 0.95:
    audio_denoised /= peak

# Save to disk (float32 or int16)
sf.write(ESP_NORM_PATH, audio_denoised, target_sr, subtype="PCM_16")
print("\nSaved cleaned audio to:", ESP_NORM_PATH, "\n")
