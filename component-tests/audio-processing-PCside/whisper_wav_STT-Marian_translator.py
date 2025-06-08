import whisper
from transformers import MarianMTModel, MarianTokenizer
from my_local_paths import ESP_WAV_PATH, ESP_NORM_PATH

SRC_LANG = "ar"  # Source language (Arabic)

# Use Whisper to transcribe audio to text
model = whisper.load_model("small")
transcribed_result = model.transcribe(ESP_NORM_PATH, language=SRC_LANG)
src_text = [transcribed_result["text"]]

# Use MarianMT to translate (input text) to the desired (output text) language
tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-ar-en")
model = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-ar-en")
translated = model.generate(**tokenizer(src_text, return_tensors="pt", padding=True))

print("\n", src_text)
print(tokenizer.decode(translated[0], skip_special_tokens=True))


"""
Expected Output:
Alif-un (the letter) the rabbit, it runs and it plays
it eats a carrot so it doesn't get tired.

Ba-un (the letter) the duck, it jumped a jump
it fell and the cat laughed at it.

Alif-un (the letter) the rabbit, it runs and it plays
it eats a carrot so it doesn't get tired.
===========

ESP WAV output:
[' ألف أرمد يأكل جزرا كي لا يبعض بقم بطط نطط نطط وأعط وضحة من هذه القطة']
A thousand ambers eat carrots so they don't get some bounced potatoes and give a little bit of this cat.

----------------
Normed ESP WAV output:
[' ألف أرنب يجري العز يأكل زرا كي لا يبعض بقم بطط مطط وقعت وتحكت من هذه القطة ألف أرنب يجري العز يأكل زرا كي لا يبعض']
A thousand bunnies running the goat eat a button so that they don't have some rubber potatoes that fell out of this cat,
and a thousand rabbits that go through the goat eat a button so that they don't.
"""
