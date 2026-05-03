import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import parselmouth
from parselmouth.praat import call
from scipy.signal import find_peaks

from disvoice.prosody import Prosody
from disvoice.replearning import RepLearning
import pandas as pd
from disvoice.articulation import Articulation


# Carregar o arquivo de áudio
y, sr = librosa.load('exercicio_2.wav')

# Calcular o espectrograma de STFT
D = np.abs(librosa.stft(y))
D_dB = librosa.amplitude_to_db(D, ref=np.max)

# Calcular o espectrograma de Mel
S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
S_dB = librosa.power_to_db(S, ref=np.max)

# Plotar o espectrograma de STFT
plt.figure(figsize=(12, 6))
plt.subplot(2, 1, 1)
librosa.display.specshow(D_dB, sr=sr, x_axis='time', y_axis='log')
plt.colorbar(format='%+2.0f dB')
plt.title('Espectrograma de STFT')

# Plotar o espectrograma de Mel
plt.subplot(2, 1, 2)
librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='mel')
plt.colorbar(format='%+2.0f dB')
plt.title('Espectrograma de Mel')

plt.tight_layout()
plt.show()

# Calcular a intensidade (RMS)
rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]
rms = rms*1000
# Criar um vetor de tempo para o eixo x
times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=512)

# Plotar a intensidade da fala
plt.figure(figsize=(10, 6))
plt.plot(times, rms, label='Intensidade da Fala (RMS)', color='r')
plt.xlabel('Tempo (s)')
plt.ylabel('Intensidade (RMS)')
plt.title('Intensidade da Fala ao Longo do Tempo')
plt.legend()
plt.grid()
plt.savefig('../Grafico/grafico_de_EnergiaIntensidade.png')
plt.show()

# Calcular a intensidade (energia) do sinal de áudio
frame_length = 2048
hop_length = 512
energy = np.array([
    sum(abs(y[i:i+frame_length]**2))
    for i in range(0, len(y), hop_length)
])

# Criar um vetor de tempo para o eixo x
times = librosa.frames_to_time(np.arange(len(energy)), sr=sr, hop_length=hop_length)

# Plotar a intensidade da fala
plt.figure(figsize=(10, 6))
plt.plot(times, energy, label='Intensidade da Fala', color='r')
plt.xlabel('Tempo (s)')
plt.ylabel('Intensidade (Energia)')
plt.title('Intensidade da Fala ao Longo do Tempo')
plt.legend()
plt.grid()
plt.show()

def jitter(y, sr):
    # Calcular a diferença entre períodos consecutivos
    periods = librosa.effects.split(y, top_db=20)
    diffs = np.diff(periods)
    return np.mean(diffs) / np.mean(periods)

def shimmer(y, sr):
    # Calcular a diferença entre amplitudes consecutivas
    amplitudes = np.abs(y)
    diffs = np.diff(amplitudes)
    return np.mean(diffs) / np.mean(amplitudes)

jitter_value = jitter(y, sr)
shimmer_value = shimmer(y, sr)
print("====================Usando Librosa====================")

#Pich
pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr)
pitch_v = pitches[magnitudes > np.median(magnitudes)]

# Calcular o espectro de frequência
spectrum = np.abs(np.fft.rfft(y))
freqs = np.fft.rfftfreq(len(y), 1/sr)

# Encontrar picos no espectro
peaks, _ = find_peaks(spectrum, height=0.1)
formants = freqs[peaks]

print(f"Pitch: {pitch_v}")
print(f"Intensidade: {rms}")
print(f"Formantes: {formants}")
print(f"Jitter: {jitter_value} " )
print(f"Shimmer: {shimmer_value} ")

print("====================Usando Pramout=====================")
# Carregar o áudio usando parselmouth
snd = parselmouth.Sound('exercicio_2.wav')

# Extrair pitch
pitch = snd.to_pitch()
pitch_values = pitch.selected_array['frequency']

# Extrair intensidade
intensity = snd.to_intensity()
intensity_values = intensity.values.T

times = librosa.frames_to_time(np.arange(len(intensity_values)), sr=sr, hop_length=hop_length)

# Plotar a intensidade da fala
plt.figure(figsize=(10, 6))
plt.plot(times, intensity_values, label='Intensidade da Fala Pramout (RMS)', color='r')
plt.xlabel('Tempo (s)')
plt.ylabel('Intensidade (RMS)')
plt.title('Intensidade da Fala ao Longo do Tempo')
plt.legend()
plt.grid()
plt.savefig('../Grafico/grafico_de_IntensidadePrarsrlMOuth.png')
plt.show()

# Extrair formantes
formants = snd.to_formant_burg()

times = np.linspace(0, snd.get_total_duration(), formants.get_number_of_frames())

# Obter os valores dos formantes
f1 = [formants.get_value_at_time(1, t) for t in times]
f2 = [formants.get_value_at_time(2, t) for t in times]
f3 = [formants.get_value_at_time(3, t) for t in times]
 #================ Plotar os formantes ==========================
plt.figure(figsize=(10, 6))
plt.plot(times, f1, label='F1', color='r')
plt.plot(times, f2, label='F2', color='g')
plt.plot(times, f3, label='F3', color='b')
plt.xlabel('Tempo (s)')
plt.ylabel('Frequência (Hz)')
plt.title('Formantes ao Longo do Tempo')
plt.legend()
plt.grid()
plt.savefig('../Grafico/grafico_de_formantes.png')
plt.show()

# Converter para PointProcess
point_process = parselmouth.praat.call(snd, "To PointProcess (periodic, cc)...", 75, 600)

# Calcular Jitter
jitter_local = parselmouth.praat.call(point_process, "Get jitter (local)...", 0, 0, 0.0001, 0.02, 1.3)

# Calcular Shimmer
shimmer_local = parselmouth.praat.call([snd, point_process], "Get shimmer (local)...", 0, 0, 0.0001, 0.02, 1.3, 1.6)

# Extrair jitter e shimmer
#point_process = snd.to_point_process()
#jitter_local = point_process.get_jitter_local()
#shimmer_local = point_process.get_shimmer_local()

# Exibir resultados
print(f"Pitch: {pitch_values}")
print(f"Intensidade: {intensity_values}")
print(f"Formantes: ")
print(f"Jitter: {jitter_local}")
print(f"Shimmer: {shimmer_local}")

#=============================================
# Carregar o arquivo de áudio
#snd = parselmouth.Sound('seu_arquivo_de_audio.wav')
def fake_show():
    pass  # Não faz nada


#########################################################################################
# Detectar pausas (silêncios)
intervals = librosa.effects.split(y, top_db=20)

# Calcular a duração total de fala ativa
total_sounding_duration = sum((end - start) / sr for start, end in intervals)

# Contar o número de sílabas (simplificação: número de picos de energia)
onset_env = librosa.onset.onset_strength(y=y, sr=sr)
peaks = librosa.util.peak_pick(onset_env, pre_max=20, post_max=20, pre_avg=50, post_avg=50, delta=0.2, wait=10)

# Calcular a taxa de articulação
articulation_rate = len(peaks) / total_sounding_duration

# Exibir resultados
print(f"Taxa de Articulação: {articulation_rate} sílabas por segundo")

# Detectar pausas (silêncios)
intervals = librosa.effects.split(y, top_db=20)
# Calcular a duração total do áudio
total_duration = len(y) / sr

# Calcular a duração total de fala ativa
total_sounding_duration = sum((end - start) / sr for start, end in intervals)

# Calcular a duração total das pausas
total_pause_duration = total_duration - total_sounding_duration

# Exibir resultados
print(f"Duração total das pausas: {total_pause_duration} segundos")
print(f"Numero total das pausas: {len(intervals)}")
#===================================================================###################======================================#################===============#=============

print("===================================================================================")
print("Usando Divoice Library:")
print("===================================================================================")
# Substituir temporariamente plt.show() pela função fake


plt.show = fake_show
# Criar instância do módulo de prosódia
prosody = Prosody()

# Caminho do arquivo de áudio
audio_path = "exercicio_2.wav"

# Extrair características
features = prosody.extract_features_file(audio_path, static=False, plots=True, fmt='dataframe' )
"""
# Agora podemos capturar os gráficos
for i, fig_num in enumerate(plt.get_fignums()):
    fig = plt.figure(fig_num)
    fig.savefig(f"prosody_graph_{i+1}.png", dpi=300, bbox_inches="tight")
plt.show()
"""

# Mostrar os primeiros valores extraídos
print(features)
print("===========================Pandas==COLUNA POR COLUNA=============================")
df = pd.DataFrame(features)

# Preparar uma lista para os documentos
documentos = []
documento = {}
i = -1
# Iterar pelas linhas do DataFrame
for _, linha in df.iterrows():
    i +=1
    for coluna in df.columns:  # Iterar pelas colunas
        if i == 0:
            documento[coluna] = [linha[coluna]]
        else:
            documento[coluna].append(linha[coluna])  # Adicionar chave (coluna) e valor

documentos.append(documento)

print(documentos)


df = df.to_json(orient='table')
#print(df)

features1 = prosody.extract_features_file(audio_path, static=False, plots=True, fmt='dataframe')
#fig = plt.gcf()
#fig.savefig("../Grafico/prosody_graph1.png", dpi=300, bbox_inches="tight")

print("=====================DataFrame=================")
print(features1)

replearning = RepLearning('CAE')

# Extração de características de aprendizagem de representação
features = replearning.extract_features_file(audio_path, static=True, fmt ='dataframe')
print(features)
print("==============================================")
# Extração de características de aprendizagem de representação
features = replearning.extract_features_file(audio_path, static=False, fmt ='dataframe')
print(features)

def articulationFeatures (audio):
        plt.show = fake_show
        articulation = Articulation()
        print(":::::::::::::::::::::::Articulação 0")
        featuresStatic = articulation.extract_features_file(audio, static=True, plots=True, fmt='dataframe' )
        print(":::::::::::::::::::::::Articulação 1")
        featuresNoStatic = articulation.extract_features_file(audio, static=False, plots=True, fmt='dataframe' )
        print(":::::::::::::::::::::::Articulação 2")
        for i, fig_num in enumerate(plt.get_fignums()):
            fig = plt.figure(fig_num)
            fig.savefig(f"../Grafico/articulation_graph_{i+1}.png", dpi=300, bbox_inches="tight")
        print(featuresNoStatic)

articulationFeatures("exercicio_1.wav")

"""""
# Caminho para o arquivo de áudio
#audio_file = "exercicio_2.wav"

# Inicializar a classe DisVoice
prosody = DisVoice()

# Extrair características prosódicas
prosodic_features = prosody.extract_features(y)

# Converter para DataFrame para visualização
df = pd.DataFrame(prosodic_features)
print(df.head())
print("===================================================================================")
print(f"prosody features: {prosodic_features}")

PATH=os.path.dirname(os.path.realpath(__file__))

PATH_DISVOICE=os.path.dirname(os.path.realpath(__file__))+"/disvoice/"
sys.path.append(PATH_DISVOICE)
"""""


