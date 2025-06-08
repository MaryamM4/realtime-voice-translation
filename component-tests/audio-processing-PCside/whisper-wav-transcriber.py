import whisper
from my_local_paths import PC_WAV_PATH, ESP_WAV_PATH, ESP_NORM_PATH

LANG = "ar"  # Set to None for auto detection (detection uses 30 seconds), or "ar" for arabic

# Whisper transcription
model = whisper.load_model("small")
result = model.transcribe(ESP_WAV_PATH, language=LANG, verbose=True)
print("\n", result["text"], "\n")

"""
RESULTS

brief_arab_sample vs normalized_resampled Outputs (language="ar"):
ألف أرنب يجري يلعب كل ززرا كي لا يتعب باء بططة ونطط نطط وقعت ضحكت منها القطة
ألف أرنم يجري يلعب يأكل ززراً كي لا يتعب باء بططة ونطط نطط وقعت ضحكت منها القطة

Orginial preformed better than processed. 

-------------------
brief_arab_sample language="ar" vs None Outputs:
ألف أرنب يجري يلعب كل ززرا كي لا يتعب باء بططة ونطط نطط وقعت ضحكت منها القطة
ألف أرنب يجري يلعب كل ززرا كي لا يتعب باء بططة ونطط نطط وقعت ضحكت منها القطة

Auto preformed just fine, but had a 30 second cost. 

-------------------
debug_chunk (clip from ESP audio) Output:
Auto detected English...
No more Cesare Up сколько de tiempoope maятно zwISS

language="ar":
هذة صحية المَن What are thi A

-------------------
esp_audio Output:
Detected language: Arabic
لف أرمد يأكل جزرا كي لا يبعض بقم بطط نطط نطط وأعط وضحة من هذه القطة

language="ar"
ألف أرمد يأكل جزرا كي لا يبعض بقم بطط نطط نطط وأعط وضحة من هذه القطة

They're missing a portion from the end.
-------------------
normed_esp_audio Output:
Detected Arabic
ألف أرنب يجري العز يأكل زرا كي لا يبعض بقم بطط مطط وقعت وتحكت من هذه القطة ألف أرنب يجري العز يأكل زرا كي لا يبعض

language="ar"
ألف أرنب يجري العز يأكل زرا كي لا يبعض بقم بطط مطط وقعت وتحكت من هذه القطة ألف أرنب يجري العز يأكل زرا كي لا يبعض

"""
