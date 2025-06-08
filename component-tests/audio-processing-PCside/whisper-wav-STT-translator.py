# Transcribes and translates
# Whisper only translates to english

import whisper
from my_local_paths import ESP_WAV_PATH, ESP_NORM_PATH

LANG = "ar"  # Source language ("ar" for Arabic, None for auto)
MODEL_SIZE = "large-v3"  # tiny, base, small, medium, large, large-v2, large-v3

# To delete the model, navigate to the directory:
# C:\Users\<user>\.cache\whisper
# and delete the .pt files.

model = whisper.load_model(MODEL_SIZE)

# Translate speech to English text
result = model.transcribe(ESP_WAV_PATH, language=LANG, task="translate", verbose=True)

print("\nTranslated to English:\n", result["text"], "\n")


"""
Expected Output:
Alif-un (the letter) the rabbit, it runs and it plays
it eats a carrot so it doesn't get tired.

Ba-un (the letter) the duck, it jumped a jump
it fell and the cat laughed at it.

Alif-un (the letter) the rabbit, it runs and it plays
it eats a carrot so it doesn't get tired.

===========
ESP WAV output (large-v3 model):)
A thousand rabbits run and play, eating fruits so they don't get tired.
A duck was running and running, and a cat sat and laughed at it.
A thousand rabbits run and play, eating fruits so they don't get tired.

----------------
ESP WAV output (small model):
A thousand ants, oh Lord, eat a seed so it can grow.
It's a plant, a plant, a plant, and I've found a seed from this plant.
A thousand ants, oh Lord, eat a seed so it can grow.

----------------
Normed ESP WAV output (small model):
A thousand ants, what a pity! They eat a tree to make it sit,
they cover it, cover it, cover it and cover it, and cover it from this cover.
A thousand ants, what a pity! They eat a tree to make it sit.
"""
