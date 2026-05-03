#Claro! Aqui estão alguns exemplos de como analisar alguns dos parâmetros mencionados usando Python e bibliotecas como `librosa` e `pydub`.

### Frequência Fundamental (Pitch) com `librosa`

#```python
import librosa
import numpy as np

# Carregar o arquivo de áudio
audio_path = 'seu_audio.wav'
y, sr = librosa.load(audio_path)

# Extrair a frequência fundamental (pitch)
pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
pitch = []

for t in range(pitches.shape[1]):
    index = magnitudes[:, t].argmax()
    pitch.append(pitches[index, t])

# Filtrar zeros
pitch = [p for p in pitch if p > 0]

# Imprimir as frequências encontradas
print(np.array(pitch))


### Intensidade (Loudness) com `pydub`

#```python
from pydub import AudioSegment
from pydub.utils import mediainfo

# Carregar o arquivo de áudio
audio = AudioSegment.from_file('seu_audio.wav')

# Calcular a intensidade média em dBFS (Decibéis em Escala Full Scale)
loudness = audio.dBFS

# Imprimir a intensidade média
print(f"Intensidade média: {loudness} dBFS")


### Formantes usando `librosa` e `praat-parselmouth`

#```python
import parselmouth
from parselmouth.praat import call
import numpy as np

# Carregar o arquivo de áudio
sound = parselmouth.Sound("seu_audio.wav")

# Analisar os formantes
formants = call(sound, "To Formant (burg)", 0.0, 5.0, 5500, 0.025, 50.0)

# Extrair valores dos formantes
formant_values = []
for t in range(1, int(formants.get_total_duration()) + 1):
    formant_values.append([call(formants, "Get value at time", formant, t, "Hertz") for formant in range(1, 4)])

# Imprimir os formantes
print(np.array(formant_values))


#Estes são exemplos básicos e podem precisar ser ajustados conforme a sua aplicação específica. Se precisar de mais detalhes ou exemplos adicionais, sinta-se à vontade para perguntar!