import pyworld
import numpy as np
import soundfile as sf

import parselmouth

import librosa
import matplotlib.pyplot as plt

import os
import json



diagnostico = {}
# Load a speech waveform
x, fs = sf.read("REPA_REPADI_2.wav")  # Replace with your .wav file

# Analyze the speech
f0, sp, ap = pyworld.wav2world(x, fs)  # Extract F0, spectral envelope, and aperiodicity

# f0_, t = pyworld.dio(x,fs)

# print(f0_)


# Synthesize speech
synthesized = pyworld.synthesize(f0, sp, ap, fs)

f0 = f0[np.where(f0 > 0)[0]]  # remover valores null

print(f"F0 type: {type(f0)}")

#Print:
print(f"F0: {f0}")
print(f"LenF0: {len(f0)}")
print(f"max: {max(f0)}")
print(f"min: {min(f0)}")
print("____________________________________")
print(f"sp: {sp}")
print("____________________________________")
print(f"fs: {fs}")
print("____________________________________")
# for data in f0:
#     print(data)


# Save the synthesized speech
sf.write("synthesized.wav", synthesized, fs)



def fundamentalFrequency_F0(audio):

        y, sr = librosa.load(audio)  # Carregar o audio
        f0, voiced_flag, voiced_probs = librosa.pyin(y=y,sr=sr,fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
        
        f0 = f0[~np.isnan(f0)]  # remover valores de NaN

        # calcular pitch medio: 
        medium_pitch = np.mean(f0)

        # calcular variação do pitch ao longo do tempo:
        pitch_variation = np.std(f0)

        #calcular frequencia mundamental maxima
        maxF0 = max(f0)

        #calcular frequência fundamental minima
        minF0 = min(f0)

        diagnostico['frequencia fundamental'] = f0
        diagnostico['pitch_medio'] = medium_pitch
        diagnostico['varicao_pitch'] = pitch_variation
        diagnostico['frequencia_fundamental_maxima'] = maxF0
        diagnostico['frequencia_fundamental_minima'] = minF0

        print("diagnostico: ",diagnostico)

        makeF0Plot(y=y,sr=sr)



def makeF0Plot(y,sr):
        times = librosa.times_like(diagnostico['frequencia fundamental'], sr=sr)

        D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
        fig, ax = plt.subplots()
        img = librosa.display.specshow(D, x_axis='time', y_axis='hz', ax=ax)
        plt.title('Estimativa de Frequência Fundamental (f0)')
        plt.colorbar(img, ax=ax, format="%+2.f dB")
        plt.plot(times, diagnostico['frequencia fundamental'], label='f0', color='cyan', linewidth=3)
        plt.legend(loc='upper right')
        # plt.savefig('../../Grafico/grafico_de_frequencia_fundamental.png')
        plt.show()


audio1 = "REPA_REPADI_2.wav"
fundamentalFrequency_F0(audio1)


# Step 1: Load audio with full precision
audio, sr = sf.read(audio1, dtype='float64')

# Step 2: Convert to mono if needed
if audio.ndim > 1:
    audio = audio.mean(axis=1)

# Step 3: Extract F₀ using WORLD
_f0, t = pyworld.dio(audio.astype('float64'), sr)     # Initial F₀ estimation
f0_v1 = pyworld.stonemask(audio.astype('float64'), _f0, t, sr)  # Refined F₀
f0_v1 = f0_v1[np.where(f0_v1 > 0)[0]]
print("::::::::::::::::::::::::::::::::::::::")
print(f"newF0: {f0_v1}")

def pause_duration_over_time(audio):
    y, sr = librosa.load(audio)  # Load audio
    intervals = librosa.effects.split(y, top_db=20)  # Sounding intervals

    total_duration = len(y) / sr
    total_sounding_duration = sum((end - start) / sr for start, end in intervals)
    total_pause_duration = total_duration - total_sounding_duration

    print(f"Total duration: {total_duration:.2f} sec")
    print(f"Total sounding duration: {total_sounding_duration:.2f} sec")
    print(f"Total pause duration: {total_pause_duration:.2f} sec")

    # 🔍 Get pause intervals by inverting sounding intervals
    pause_intervals = []
    prev_end = 0
    for start, end in intervals:
        if start > prev_end:
            pause_intervals.append((prev_end, start))
        prev_end = end
    if prev_end < len(y):
        pause_intervals.append((prev_end, len(y)))

    # 🕒 Convert to seconds and print
    pause_durations = [(start / sr, end / sr, (end - start) / sr) for start, end in pause_intervals]
    print("\nPause durations over time:")
    for i, (start_sec, end_sec, dur_sec) in enumerate(pause_durations):
        print(f"Pause {i+1}: Start = {start_sec:.2f}s, End = {end_sec:.2f}s, Duration = {dur_sec:.2f}s")

    return pause_durations

pause_duration_over_time(audio1)


def detectar_tmf_auto(audio_path):
    snd = parselmouth.Sound(audio_path)
    intensity = snd.to_intensity()

    # Calcula a média da intensidade (ignorando valores nulos)
    valores = [intensity.get_value(time=t) for t in intensity.xs()]
    valores_validos = [v for v in valores if v is not None]
    media_db = sum(valores_validos) / len(valores_validos)

    # Define o limiar como 60% da média (ajustável)
    threshold_db = media_db * 0.6

    print(f"Limiar automático: {threshold_db:.2f} dB")

    start_time = None
    end_time = None

    # print("Intensidade: ", intensity)


    for t in intensity.xs():
        valor = intensity.get_value(time=t)
        if valor and valor > threshold_db:
            if start_time is None:
                start_time = t
            end_time = t

    if start_time and end_time:
        tmf = end_time - start_time
        print(f"TMF estimado: {tmf:.2f} segundos")
        return tmf
    else:
        print("Não foi possível detectar fonação.")
        return None
    


def extrair_intensidade(audio_path):
    snd = parselmouth.Sound(audio_path)
    intensity = snd.to_intensity()
    tempos = intensity.xs()
    valores = [intensity.get_value(time=t) or 0 for t in tempos]

    print("Intensidade2: ", intensity)
    return tempos, valores

def plotar_comparativo(audio_files, nomes_sessoes, paciente_id):
    plt.figure(figsize=(10, 6))
    for audio, nome in zip(audio_files, nomes_sessoes):
        tempos, valores = extrair_intensidade(audio)
        plt.plot(tempos, valores, label=nome)

    plt.title(f"Comparativo de Intensidade Vocal - {paciente_id}")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Intensidade (dB)")
    plt.legend()
    plt.grid(True)
    output_path = f"graficos/{paciente_id}_intensidade.png"
    plt.savefig(output_path)
    plt.close()
    print(f"Gráfico salvo em: {output_path}")

# Exemplo de uso
audio_dir = "./"
paciente_id = "paciente1"
audio_files = [
    os.path.join(audio_dir, "REPA_REPADI_2.wav"),
    os.path.join(audio_dir, "REPA_REPADI_1.wav"),
    os.path.join(audio_dir, "exercicio_3.wav")
]
nomes_sessoes = ["Sessão 1", "Sessão 2", "Sessão 3"]

# plotar_comparativo(audio_files, nomes_sessoes, paciente_id)



    
    

# Exemplo de uso
detectar_tmf_auto(audio1)

# extrair_intensidade(audio1)


# def extrair_e_plotar_intensidade(caminho_audio):
#     """
#     Extrai a intensidade (em dB) de um arquivo de áudio e plota ao longo do tempo.

#     Parâmetros:
#     - caminho_audio: str, caminho para o arquivo .wav

#     Retorna:
#     - None (exibe o gráfico)
#     """
#     # Carrega o áudio
#     som = parselmouth.Sound(caminho_audio)

#     # Extrai a intensidade
#     intensidade = som.to_intensity()

#     # Obtém tempo e valores de intensidade
#     tempos = intensidade.xs()
#     valores_db = intensidade.values.T.flatten()

#     # Plot
#     plt.figure(figsize=(10, 4))
#     plt.plot(tempos, valores_db, color='darkorange')
#     plt.title("Intensidade Vocal ao Longo do Tempo")
#     plt.xlabel("Tempo (s)")
#     plt.ylabel("Intensidade (dB)")
#     plt.grid(True)
#     plt.tight_layout()
#     plt.show()


# extrair_e_plotar_intensidade(audio1)


# # Load your audio file
# sound = parselmouth.Sound(audio1)

# # # Run voice activity detection using Praat's "To TextGrid (silences)..."
# # textgrid = parselmouth.praat.call(sound, "To TextGrid (silences)", 
# #                                   100.0, 0.0, 0.1, 0.05, "silent", "sounding")

# textgrid = parselmouth.praat.call(sound, "To TextGrid (silences)", -25, 0.1, 0.1,0.05,0.05, "silent", "sounding")


# # Extract the "silent" intervals from the TextGrid
# interval_tier = textgrid.get_tier_by_name("silent")

# # Loop through intervals and get pause durations
# pause_durations = []
# for i in range(interval_tier.number_of_intervals):
#     interval = interval_tier.get_interval(i)
#     duration = interval.xmax - interval.xmin
#     if duration > 0:
#         pause_durations.append((interval.xmin, interval.xmax, duration))

# # Print results
# for start, end, dur in pause_durations:
#     print(f"Pause from {start:.2f}s to {end:.2f}s — Duration: {dur:.2f}s")


def extrair_e_plotar_intensidade(caminho_audio, salvar_imagem=False, caminho_imagem="intensidade_plot.png"):
    """
    Extrai a intensidade (em dB) de um arquivo de áudio, plota e retorna estatísticas.

    Parâmetros:
    - caminho_audio: str, caminho para o arquivo .wav
    - salvar_imagem: bool, se True salva o gráfico como imagem
    - caminho_imagem: str, caminho para salvar a imagem

    Retorna:
    - dict com estatísticas: média, máximo, mínimo
    """
    # Carrega o áudio
    som = parselmouth.Sound(caminho_audio)

    # Extrai a intensidade
    intensidade = som.to_intensity()

    # Obtém tempo e valores de intensidade
    tempos = intensidade.xs()
    valores_db = intensidade.values.T.flatten()

    # Remove valores inválidos (zero ou negativos)
    valores_db = valores_db[valores_db > 0]

    # Estatísticas
    estatisticas = {
        "média_dB": np.mean(valores_db),
        "máximo_dB": np.max(valores_db),
        "mínimo_dB": np.min(valores_db)
    }

    # Plot
    plt.figure(figsize=(10, 4))
    plt.plot(tempos[:len(valores_db)], valores_db, color='darkorange')
    plt.title("Intensidade Vocal ao Longo do Tempo")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Intensidade (dB)")
    plt.grid(True)
    plt.tight_layout()

    # Salvar imagem se solicitado
    if salvar_imagem:
        plt.savefig(caminho_imagem)
        print(f"📁 Gráfico salvo em: {os.path.abspath(caminho_imagem)}")

    plt.show()

    return estatisticas

stats = extrair_e_plotar_intensidade(audio1, salvar_imagem=True)
print("📊 Estatísticas de Intensidade:")
for k, v in stats.items():
    print(f"{k}: {v:.2f} dB")


def gerar_json_intensidade(caminho_audio, caminho_saida="intensidade.json"):
    """
    Extrai a intensidade vocal de um arquivo .wav e salva como JSON.

    Parâmetros:
    - caminho_audio: str, caminho para o arquivo .wav
    - caminho_saida: str, caminho para salvar o JSON

    Retorna:
    - Lista de dicionários com 'time' e 'db'
    """
    som = parselmouth.Sound(caminho_audio)
    intensidade = som.to_intensity()

    tempos = intensidade.xs()
    valores_db = intensidade.values.T.flatten()

    # Remove valores inválidos (zero ou negativos)
    dados = [
        {"time": float(t), "db": float(db)}
        for t, db in zip(tempos, valores_db)
        if db > 0
    ]

    # Salva como JSON
    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2)

    print(f"✅ JSON salvo em: {os.path.abspath(caminho_saida)}")
    return dados




dados = gerar_json_intensidade(audio1, "REPA_REPADI_2.json")

# print("Dados.json:", dados)


# def analisar_terapia_fala_auto(audio_path):
#     """
#     Análise clínica adaptativa da velocidade de fala.
#     Ajusta automaticamente os limiares de intensidade e pausa.
#     """
#     snd = parselmouth.Sound(audio_path)

#     # Extração de intensidade
#     intensity = snd.to_intensity()
#     duracao_total = snd.get_total_duration()

#     time = intensity.xs()
#     values = intensity.values[0]

#     # ============================
#     # 1. Definir intensidade_min dinamicamente
#     # ============================
#     intensidade_media = np.mean(values[values > 0])  # média apenas de valores válidos
#     intensidade_min = intensidade_media - 15  # 15 dB abaixo da média

#     acima = values > intensidade_min

#     # Contagem de "picos de intensidade" ≈ sílabas
#     picos = []
#     for i in range(1, len(acima)):
#         if acima[i] and not acima[i-1]:
#             picos.append(time[i])
#     n_silabas = len(picos)

#     # ============================
#     # 2. Identificar pausas
#     # ============================
#     pausas_brutas = []
#     ultima = None
#     for i in range(len(acima)):
#         if not acima[i]:
#             if ultima is None:
#                 ultima = time[i]
#         else:
#             if ultima is not None:
#                 duracao = time[i] - ultima
#                 pausas_brutas.append(duracao)
#                 ultima = None

#     # ============================
#     # 3. Definir pausa_min dinamicamente
#     # ============================
#     if pausas_brutas:
#         pausa_min = np.percentile(pausas_brutas, 90)  # separa micro-silêncios de pausas reais
#     else:
#         pausa_min = 0.2  # fallback padrão

#     pausas = [p for p in pausas_brutas if p >= pausa_min]
#     tempo_pausas = sum(pausas)
#     tempo_falado = duracao_total - tempo_pausas

#     # ============================
#     # 4. Métricas
#     # ============================
#     sps_total = n_silabas / duracao_total if duracao_total > 0 else 0
#     sps_articulacao = n_silabas / tempo_falado if tempo_falado > 0 else 0
#     n_pausas = len(pausas)
#     pausa_media = np.mean(pausas) if pausas else 0

#     return {
#         "duração_total(s)": round(duracao_total, 2),
#         "tempo_falado(s)": round(tempo_falado, 2),
#         "sílabas": n_silabas,
#         "SPS total (sílabas/s)": round(sps_total, 2),
#         "SPS articulação (sílabas/s)": round(sps_articulacao, 2),
#         "nº pausas": n_pausas,
#         "duração média pausa(s)": round(pausa_media, 2),
#         "intensidade_min(dB)": round(intensidade_min, 2),
#         "pausa_min(s)": round(pausa_min, 2)
#     }


# def gerar_relatorio(metricas):
#     relatorio = f"""
#     📊 Relatório Clínico de Velocidade de Fala (Adaptativo)

#     ▸ Duração total: {metricas['duração_total(s)']} s
#     ▸ Tempo efetivo de fala: {metricas['tempo_falado(s)']} s

#     ▸ Número estimado de sílabas: {metricas['sílabas']}
#     ▸ Velocidade de fala (SPS total): {metricas['SPS total (sílabas/s)']} síl/s
#     ▸ Taxa de articulação (SPS fala): {metricas['SPS articulação (sílabas/s)']} síl/s

#     ▸ Número de pausas: {metricas['nº pausas']}
#     ▸ Duração média das pausas: {metricas['duração média pausa(s)']} s

#     ⚙️ Parâmetros automáticos:
#     ▸ Intensidade mínima usada: {metricas['intensidade_min(dB)']} dB
#     ▸ Pausa mínima considerada: {metricas['pausa_min(s)']} s
#     """
#     return relatorio


# # ==========
# # USO
# # ==========

# # audio = "exemplo.wav"
# metricas = analisar_terapia_fala_auto(audio1)
# print(gerar_relatorio(metricas))




# def analisar_terapia_fala_auto(audio_path):
#     snd = parselmouth.Sound(audio_path)

#     # Extração de intensidade
#     intensity = snd.to_intensity()
#     duracao_total = snd.get_total_duration()

#     time = intensity.xs()
#     values = intensity.values[0]

#     # ============================
#     # 1. Definir intensidade_min dinamicamente
#     # ============================
#     intensidade_media = np.mean(values[values > 0])
#     intensidade_min = intensidade_media - 15

#     acima = values > intensidade_min

#     # Contagem de "picos de intensidade" ≈ sílabas
#     picos = []
#     for i in range(1, len(acima)):
#         if acima[i] and not acima[i-1]:
#             picos.append(time[i])
#     n_silabas = len(picos)

#     # ============================
#     # 2. Identificar pausas
#     # ============================
#     pausas_brutas = []
#     ultima = None
#     for i in range(len(acima)):
#         if not acima[i]:
#             if ultima is None:
#                 ultima = time[i]
#         else:
#             if ultima is not None:
#                 duracao = time[i] - ultima
#                 pausas_brutas.append((ultima, time[i], duracao))
#                 ultima = None

#     # ============================
#     # 3. Definir pausa_min dinamicamente
#     # ============================
#     if pausas_brutas:
#         pausa_min = np.percentile([p[2] for p in pausas_brutas], 90)
#     else:
#         pausa_min = 0.2

#     pausas = [(ini, fim, dur) for ini, fim, dur in pausas_brutas if dur >= pausa_min]
#     tempo_pausas = sum([dur for _, _, dur in pausas])
#     tempo_falado = duracao_total - tempo_pausas

#     # ============================
#     # 4. Métricas
#     # ============================
#     sps_total = n_silabas / duracao_total if duracao_total > 0 else 0
#     sps_articulacao = n_silabas / tempo_falado if tempo_falado > 0 else 0
#     n_pausas = len(pausas)
#     pausa_media = np.mean([dur for _, _, dur in pausas]) if pausas else 0

#     metricas = {
#         "duração_total(s)": round(duracao_total, 2),
#         "tempo_falado(s)": round(tempo_falado, 2),
#         "sílabas": n_silabas,
#         "SPS total (sílabas/s)": round(sps_total, 2),
#         "SPS articulação (sílabas/s)": round(sps_articulacao, 2),
#         "nº pausas": n_pausas,
#         "duração média pausa(s)": round(pausa_media, 2),
#         "intensidade_min(dB)": round(intensidade_min, 2),
#         "pausa_min(s)": round(pausa_min, 2),
#         "picos": picos,
#         "pausas": pausas,
#         "time": time,
#         "intensity": values
#     }
#     return metricas, snd


# def plotar_analise(metricas, snd):
#     fig, axs = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

#     # ===== Onda sonora =====
#     axs[0].plot(snd.xs(), snd.values[0], color="black")
#     axs[0].set_title("Onda Sonora")
#     axs[0].set_ylabel("Amplitude")

#     # Pausas sobre onda
#     for ini, fim, _ in metricas["pausas"]:
#         axs[0].axvspan(ini, fim, color="red", alpha=0.3)

#     # ===== Intensidade =====
#     axs[1].plot(metricas["time"], metricas["intensity"], color="blue", label="Intensidade (dB)")
#     axs[1].axhline(metricas["intensidade_min(dB)"], color="orange", linestyle="--", label="Limiar intensidade")

#     # Marcar sílabas (picos)
#     axs[1].scatter(metricas["picos"], [metricas["intensidade_min(dB)"]+5]*len(metricas["picos"]), 
#                    color="green", marker="o", label="Sílabas")

#     # Pausas
#     for ini, fim, _ in metricas["pausas"]:
#         axs[1].axvspan(ini, fim, color="red", alpha=0.3, label="Pausa" if ini == metricas["pausas"][0][0] else "")

#     axs[1].set_title("Intensidade com Detecção de Sílabas e Pausas")
#     axs[1].set_ylabel("Intensidade (dB)")
#     axs[1].set_xlabel("Tempo (s)")
#     axs[1].legend()

#     plt.tight_layout()
#     plt.show()


# # ==========
# # USO
# # ==========

# # audio = "exemplo.wav"
# metricas, snd = analisar_terapia_fala_auto(audio1)
# for k, v in metricas.items():
#     if k not in ["picos", "pausas", "time", "intensity"]:
#         print(f"{k}: {v}")

# plotar_analise(metricas, snd)



# def analisar_terapia_fala_auto(audio_path):
#     snd = parselmouth.Sound(audio_path)
#     duracao_total = snd.get_total_duration()

#     # ===== Intensidade =====
#     intensity = snd.to_intensity()
#     time = intensity.xs()
#     intensity_values = intensity.values[0]

#     # ===== Pitch =====
#     pitch = snd.to_pitch()
#     pitch_values = [pitch.get_value_at_time(t) or 0 for t in time]

#     # ===== Limiares dinâmicos =====
#     intensidade_media = np.mean(intensity_values[intensity_values > 0])
#     intensidade_min = intensidade_media - 15
#     pitch_min = 75  # Hz, pode ser ajustado ou definido dinamicamente

#     # ===== Detecção de sílabas =====
#     acima = [(i > intensidade_min and f0 > pitch_min) for i, f0 in zip(intensity_values, pitch_values)]
#     picos = []
#     for i in range(1, len(acima)):
#         if acima[i] and not acima[i-1]:
#             picos.append(time[i])
#     n_silabas = len(picos)

#     # ===== Identificação de pausas =====
#     pausas_brutas = []
#     ultima = None
#     for i in range(len(acima)):
#         if not acima[i]:
#             if ultima is None:
#                 ultima = time[i]
#         else:
#             if ultima is not None:
#                 duracao = time[i] - ultima
#                 pausas_brutas.append((ultima, time[i], duracao))
#                 ultima = None

#     pausa_min = np.percentile([p[2] for p in pausas_brutas], 90) if pausas_brutas else 0.2
#     pausas = [(ini, fim, dur) for ini, fim, dur in pausas_brutas if dur >= pausa_min]

#     tempo_pausas = sum([dur for _, _, dur in pausas])
#     tempo_falado = duracao_total - tempo_pausas

#     # ===== Métricas =====
#     sps_total = n_silabas / duracao_total if duracao_total > 0 else 0
#     sps_articulacao = n_silabas / tempo_falado if tempo_falado > 0 else 0
#     n_pausas = len(pausas)
#     pausa_media = np.mean([dur for _, _, dur in pausas]) if pausas else 0

#     metricas = {
#         "duração_total(s)": round(duracao_total, 2),
#         "tempo_falado(s)": round(tempo_falado, 2),
#         "sílabas": n_silabas,
#         "SPS total (sílabas/s)": round(sps_total, 2),
#         "SPS articulação (sílabas/s)": round(sps_articulacao, 2),
#         "nº pausas": n_pausas,
#         "duração média pausa(s)": round(pausa_media, 2),
#         "intensidade_min(dB)": round(intensidade_min, 2),
#         "pitch_min(Hz)": pitch_min,
#         "pausa_min(s)": round(pausa_min, 2),
#         "picos": picos,
#         "pausas": pausas,
#         "time": time,
#         "intensity": intensity_values,
#         "pitch": pitch_values
#     }
#     return metricas, snd

# def plotar_analise(metricas, snd):
#     fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

#     # ===== Onda sonora =====
#     axs[0].plot(snd.xs(), snd.values[0], color="black")
#     axs[0].set_title("Onda Sonora")
#     axs[0].set_ylabel("Amplitude")
#     for ini, fim, _ in metricas["pausas"]:
#         axs[0].axvspan(ini, fim, color="red", alpha=0.3)

#     # ===== Intensidade =====
#     axs[1].plot(metricas["time"], metricas["intensity"], color="blue", label="Intensidade (dB)")
#     axs[1].axhline(metricas["intensidade_min(dB)"], color="orange", linestyle="--", label="Limiar intensidade")
#     axs[1].scatter(metricas["picos"], [metricas["intensidade_min(dB)"]+5]*len(metricas["picos"]),
#                    color="green", marker="o", label="Sílabas")
#     for ini, fim, _ in metricas["pausas"]:
#         axs[1].axvspan(ini, fim, color="red", alpha=0.3, label="Pausa" if ini == metricas["pausas"][0][0] else "")
#     axs[1].set_title("Intensidade com Sílabas e Pausas")
#     axs[1].set_ylabel("Intensidade (dB)")
#     axs[1].legend()

#     # ===== Pitch =====
#     axs[2].plot(metricas["time"], metricas["pitch"], color="purple", label="Pitch (F0)")
#     axs[2].axhline(metricas["pitch_min(Hz)"], color="orange", linestyle="--", label="Limiar pitch")
#     axs[2].set_title("Pitch (F0)")
#     axs[2].set_ylabel("Frequência (Hz)")
#     axs[2].set_xlabel("Tempo (s)")
#     axs[2].legend()

#     plt.tight_layout()
#     plt.show()


# # ==========
# # USO
# # ==========
# # if __name__ == "__main__":
# #     audio = "exemplo.wav"
# metricas, snd = analisar_terapia_fala_auto(audio1)
# for k, v in metricas.items():
#     if k not in ["picos", "pausas", "time", "intensity", "pitch"]:
#         print(f"{k}: {v}")

# plotar_analise(metricas, snd)



# import parselmouth
# import numpy as np
# import matplotlib.pyplot as plt

# def analisar_terapia_fala_avancado(audio_path):
#     snd = parselmouth.Sound(audio_path)

#     # ===== Intensidade =====
#     intensity = snd.to_intensity()
#     duracao_total = snd.get_total_duration()
#     time_intensity = intensity.xs()
#     intensity_values = intensity.values[0]

#     # ===== Pitch =====
#     pitch = snd.to_pitch()
#     pitch_times = pitch.xs()
#     pitch_values = pitch.selected_array['frequency']

#     # Interpolar pitch para os tempos da intensidade
#     pitch_interp = np.interp(time_intensity, pitch_times, pitch_values)

#     # ============================
#     # Limiar intensidade automático
#     # ============================
#     intensidade_media = np.mean(intensity_values[intensity_values > 0])
#     intensidade_min = intensidade_media - 15  # 15 dB abaixo da média

#     # ============================
#     # Limiar pitch automático
#     # ============================
#     # Ignorando zeros (não fala)
#     pitch_nonzero = pitch_values[pitch_values > 0]
#     if len(pitch_nonzero) > 0:
#         pitch_min = np.percentile(pitch_nonzero, 10)  # por exemplo, 10º percentil
#     else:
#         pitch_min = 75  # fallback padrão

#     # ============================
#     # Detectar sílabas: intensidade + pitch
#     # ============================
#     acima = (intensity_values > intensidade_min) & (pitch_interp > pitch_min)

#     # Contagem de picos ≈ sílabas
#     picos = []
#     for i in range(1, len(acima)):
#         if acima[i] and not acima[i-1]:
#             picos.append(time_intensity[i])
#     n_silabas = len(picos)

#     # ============================
#     # Detectar pausas
#     # ============================
#     pausas_brutas = []
#     ultima = None
#     for i in range(len(acima)):
#         if not acima[i]:
#             if ultima is None:
#                 ultima = time_intensity[i]
#         else:
#             if ultima is not None:
#                 dur = time_intensity[i] - ultima
#                 pausas_brutas.append((ultima, time_intensity[i], dur))
#                 ultima = None

#     # Pausa mínima automática: 90º percentil
#     if pausas_brutas:
#         pausa_min = np.percentile([p[2] for p in pausas_brutas], 90)
#     else:
#         pausa_min = 0.2

#     pausas = [(ini, fim, dur) for ini, fim, dur in pausas_brutas if dur >= pausa_min]
#     tempo_pausas = sum([dur for _, _, dur in pausas])
#     tempo_falado = duracao_total - tempo_pausas

#     # ============================
#     # Métricas
#     # ============================
#     sps_total = n_silabas / duracao_total if duracao_total > 0 else 0
#     sps_articulacao = n_silabas / tempo_falado if tempo_falado > 0 else 0
#     n_pausas = len(pausas)
#     pausa_media = np.mean([dur for _, _, dur in pausas]) if pausas else 0

#     metricas = {
#         "duração_total(s)": round(duracao_total, 2),
#         "tempo_falado(s)": round(tempo_falado, 2),
#         "sílabas": n_silabas,
#         "SPS total (sílabas/s)": round(sps_total, 2),
#         "SPS articulação (sílabas/s)": round(sps_articulacao, 2),
#         "nº pausas": n_pausas,
#         "duração média pausa(s)": round(pausa_media, 2),
#         "intensidade_min(dB)": round(intensidade_min, 2),
#         "pitch_min(Hz)": round(pitch_min, 2),
#         "pausa_min(s)": round(pausa_min, 2),
#         "picos": picos,
#         "pausas": pausas,
#         "time": time_intensity,
#         "intensity": intensity_values,
#         "pitch": pitch_interp
#     }

#     return metricas, snd

# def plotar_analise_avancado(metricas, snd):
#     fig, axs = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

#     # ===== Onda sonora =====
#     axs[0].plot(snd.xs(), snd.values[0], color="black")
#     axs[0].set_title("Onda Sonora")
#     axs[0].set_ylabel("Amplitude")
#     for ini, fim, _ in metricas["pausas"]:
#         axs[0].axvspan(ini, fim, color="red", alpha=0.3)

#     # ===== Intensidade + pitch =====
#     axs[1].plot(metricas["time"], metricas["intensity"], color="blue", label="Intensidade (dB)")
#     axs[1].axhline(metricas["intensidade_min(dB)"], color="orange", linestyle="--", label="Limiar intensidade")
#     axs[1].scatter(metricas["picos"], [metricas["intensidade_min(dB)"]+5]*len(metricas["picos"]),
#                    color="green", marker="o", label="Sílabas")
#     for ini, fim, _ in metricas["pausas"]:
#         axs[1].axvspan(ini, fim, color="red", alpha=0.3, label="Pausa" if ini == metricas["pausas"][0][0] else "")
#     axs[1].set_title("Intensidade com Sílabas e Pausas")
#     axs[1].set_ylabel("Intensidade (dB)")
#     axs[1].set_xlabel("Tempo (s)")
#     axs[1].legend()
#     plt.tight_layout()
#     plt.show()


# # ===== USO =====
# # if __name__ == "__main__":
# #     audio = "exemplo.wav"
# metricas, snd = analisar_terapia_fala_avancado(audio1)
# for k, v in metricas.items():
#     if k not in ["picos", "pausas", "time", "intensity", "pitch"]:
#         print(f"{k}: {v}")
# plotar_analise_avancado(metricas, snd)



import parselmouth
import numpy as np
import matplotlib.pyplot as plt

def analisar_terapia_fala_silabas_rapidas(audio_path):
    snd = parselmouth.Sound(audio_path)

    # ===== Intensidade =====
    intensity = snd.to_intensity()
    duracao_total = snd.get_total_duration()
    time_intensity = intensity.xs()
    intensity_values = intensity.values[0]

    # ===== Pitch =====
    pitch = snd.to_pitch()
    pitch_times = pitch.xs()
    pitch_values = pitch.selected_array['frequency']

    # Interpolar pitch para os tempos da intensidade
    pitch_interp = np.interp(time_intensity, pitch_times, pitch_values)

    # ============================
    # Limiar intensidade automático
    # ============================
    intensidade_media = np.mean(intensity_values[intensity_values > 0])
    intensidade_min = intensidade_media - 15  # 15 dB abaixo da média

    # ============================
    # Limiar pitch automático
    # ============================
    pitch_nonzero = pitch_values[pitch_values > 0]
    if len(pitch_nonzero) > 0:
        pitch_min = np.percentile(pitch_nonzero, 10)
    else:
        pitch_min = 75

    # ============================
    # Detectar sílabas (intensidade + pitch)
    # ============================
    acima = (intensity_values > intensidade_min) & (pitch_interp > pitch_min)

    # Contagem de picos ≈ sílabas
    picos = []
    min_dist_s = 0.08  # mínimo 80 ms entre sílabas
    last_peak_time = -np.inf
    for i in range(1, len(acima)-1):
        # detectar subida de sinal acima do limiar
        if acima[i] and not acima[i-1]:
            t = time_intensity[i]
            if t - last_peak_time >= min_dist_s:
                picos.append(t)
                last_peak_time = t

    n_silabas = len(picos)

    # ============================
    # Detectar pausas
    # ============================
    pausas_brutas = []
    ultima = None
    for i in range(len(acima)):
        if not acima[i]:
            if ultima is None:
                ultima = time_intensity[i]
        else:
            if ultima is not None:
                dur = time_intensity[i] - ultima
                pausas_brutas.append((ultima, time_intensity[i], dur))
                ultima = None

    # Pausa mínima automática: 90º percentil
    if pausas_brutas:
        pausa_min = np.percentile([p[2] for p in pausas_brutas], 90)
    else:
        pausa_min = 0.2

    pausas = [(ini, fim, dur) for ini, fim, dur in pausas_brutas if dur >= pausa_min]
    tempo_pausas = sum([dur for _, _, dur in pausas])
    tempo_falado = duracao_total - tempo_pausas

    # ============================
    # Métricas
    # ============================
    sps_total = n_silabas / duracao_total if duracao_total > 0 else 0
    sps_articulacao = n_silabas / tempo_falado if tempo_falado > 0 else 0
    n_pausas = len(pausas)
    pausa_media = np.mean([dur for _, _, dur in pausas]) if pausas else 0

    metricas = {
        "duração_total(s)": round(duracao_total, 2),
        "tempo_falado(s)": round(tempo_falado, 2),
        "sílabas": n_silabas,
        "SPS total (sílabas/s)": round(sps_total, 2),
        "SPS articulação (sílabas/s)": round(sps_articulacao, 2),
        "nº pausas": n_pausas,
        "duração média pausa(s)": round(pausa_media, 2),
        "intensidade_min(dB)": round(intensidade_min, 2),
        "pitch_min(Hz)": round(pitch_min, 2),
        "pausa_min(s)": round(pausa_min, 2),
        "picos": picos,
        "pausas": pausas,
        "time": time_intensity,
        "intensity": intensity_values,
        "pitch": pitch_interp
        
    }

    return metricas, snd


# def plotar_analise_silabas_rapidas(metricas, snd):
#     fig, axs = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

#     # ===== Onda sonora =====
#     axs[0].plot(snd.xs(), snd.values[0], color="black")
#     axs[0].set_title("Onda Sonora")
#     axs[0].set_ylabel("Amplitude")
#     for ini, fim, _ in metricas["pausas"]:
#         axs[0].axvspan(ini, fim, color="red", alpha=0.3)

#     # ===== Intensidade + pitch =====
#     axs[1].plot(metricas["time"], metricas["intensity"], color="blue", label="Intensidade (dB)")
#     axs[1].axhline(metricas["intensidade_min(dB)"], color="orange", linestyle="--", label="Limiar intensidade")
#     axs[1].scatter(metricas["picos"], [metricas["intensidade_min(dB)"]+5]*len(metricas["picos"]),
#                    color="green", marker="o", label="Sílabas")
#     for ini, fim, _ in metricas["pausas"]:
#         axs[1].axvspan(ini, fim, color="red", alpha=0.3, label="Pausa" if ini == metricas["pausas"][0][0] else "")
#     axs[1].set_title("Intensidade com Sílabas Rápidas e Pausas")
#     axs[1].set_ylabel("Intensidade (dB)")
#     axs[1].set_xlabel("Tempo (s)")
#     axs[1].legend()
#     plt.tight_layout()
#     plt.show()


def plotar_analise_silabas_rapidas(metricas, snd):
    fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    # ===== Onda sonora =====
    axs[0].plot(snd.xs(), snd.values[0], color="black")
    axs[0].set_title("Onda Sonora")
    axs[0].set_ylabel("Amplitude")
    for ini, fim, _ in metricas["pausas"]:
        axs[0].axvspan(ini, fim, color="red", alpha=0.3)

    # ===== Intensidade =====
    axs[1].plot(metricas["time"], metricas["intensity"], color="blue", label="Intensidade (dB)")
    axs[1].axhline(metricas["intensidade_min(dB)"], color="orange", linestyle="--", label="Limiar intensidade")
    axs[1].scatter(metricas["picos"], [metricas["intensidade_min(dB)"]+5]*len(metricas["picos"]),
                   color="green", marker="o", label="Sílabas")
    for ini, fim, _ in metricas["pausas"]:
        axs[1].axvspan(ini, fim, color="red", alpha=0.3, label="Pausa" if ini == metricas["pausas"][0][0] else "")
    axs[1].set_title("Intensidade com Sílabas e Pausas")
    axs[1].set_ylabel("Intensidade (dB)")
    axs[1].legend()

    # ===== Pitch =====
    axs[2].plot(metricas["time"], metricas["pitch"], color="purple", label="Pitch (F0)")
    axs[2].axhline(metricas["pitch_min(Hz)"], color="orange", linestyle="--", label="Limiar pitch")
    axs[2].set_title("Pitch (F0)")
    axs[2].set_ylabel("Frequência (Hz)")
    axs[2].set_xlabel("Tempo (s)")
    axs[2].legend()

    plt.tight_layout()
    plt.show()

# ===== USO =====
# if __name__ == "__main__":
#     audio = "exemplo.wav"
metricas, snd = analisar_terapia_fala_silabas_rapidas(audio1)
for k, v in metricas.items():
    if k not in ["picos", "pausas", "time", "intensity", "pitch"]:
        print(f"{k}: {v}")
plotar_analise_silabas_rapidas(metricas, snd)

def gerar_relatorio(metricas):
    relatorio = f"""
    📊 Relatório Clínico de Velocidade de Fala (Adaptativo)

    ▸ Duração total: {metricas['duração_total(s)']} s
    ▸ Tempo efetivo de fala: {metricas['tempo_falado(s)']} s

    ▸ Número estimado de sílabas: {metricas['sílabas']}
    ▸ Velocidade de fala (SPS total): {metricas['SPS total (sílabas/s)']} síl/s
    ▸ Taxa de articulação (SPS fala): {metricas['SPS articulação (sílabas/s)']} síl/s

    ▸ Número de pausas: {metricas['nº pausas']}
    ▸ Duração média das pausas: {metricas['duração média pausa(s)']} s

    ⚙️ Parâmetros automáticos:
    ▸ Intensidade mínima usada: {metricas['intensidade_min(dB)']} dB
    ▸ Pausa mínima considerada: {metricas['pausa_min(s)']} s
    """
    return relatorio

#TODO: ORGANIZAR ISSO NO MODULO DE DataProcessor.py e enviar para o backend; 
#TODO: GUARDAR OS GRAFICOS PRODUZIDOS E ENVIAR PARA O BACKEND;


