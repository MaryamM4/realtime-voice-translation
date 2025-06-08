# https://github.com/ARBML/klaam

"""
brief_arab_sample Output (MSA vs EYG):
ألف أرنب يجري يلعب يأكل تزراً كيلا يتعب بعء بطونطط نطى و اع
أليفون ارنا بياجري يلعبي كله سذدا كه لا يتعب بأن بطا ونط نطة و

MSA was more accurate.
"""

import klaam
from klaam import SpeechRecognition
from my_local_paths import PC_WAV_PATH, ESP_WAV_PATH, ESP_NORM_PATH, KLAAM_PATH
import sys

sys.path.append(KLAAM_PATH)

"""
There are two avilable (trained) models for recognition trageting 
Modern Standard Arabic (msa) and Egyptian dialect (egy). Set with lang attribute.
"""
model = SpeechRecognition(lang="msa")


result = model.transcribe(ESP_WAV_PATH)
print(result)
# Command-lines don't support right-to-left script, so copy text elsewhere to see it properly


"""
KLAAM INSTALLATION:
----------------------------------------
git clone https://github.com/ARBML/klaam.git
cd klaam

# In requirements.txt, 
# - set PyYAML version to 6.0
# - add gdown

pip install -r requirements.txt
"""
