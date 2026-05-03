#====================================================================================================
# File Name : DataProcessor.py
# Autor : Adalberto Junior
# Date : 2025-02-28
# Version : 1.0
# Description : This module is responsible for processing the recorded audio. 
# 
# ====================================================================================================
# ====================================================================================================
# ====================================================================================================
# ====================================================================================================
from datetime import datetime
import json
import librosa
import time
import os 
import numpy as np
import matplotlib.pyplot as plt
import parselmouth
import pandas as pd
import requests
import pyworld
import soundfile as sf

from disvoice.prosody import Prosody
from disvoice.glottal import Glottal
from disvoice.articulation import Articulation
from disvoice.phonation import Phonation
from disvoice.replearning import RepLearning
from disvoice.phonological import Phonological

##====================================================================================================
# DataProcessor Class
#=====================================================================================================

class DataProcessor:

    diagnostico = {}


    def __init__(self, filename = '../Diagnostico/diagnostico.txt'):
        self.filename = filename

    # f0
    def fundamentalFrequency_F0(self, audio):

        y, sr = librosa.load(audio)  # Carregar o audio
        f0, voiced_flag, voiced_probs = librosa.pyin(y=y,sr=sr,fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
        
        f0 = f0[~np.isnan(f0)]  # remover valores de NaN

        # calcular pitch medio: 
        medium_pitch = np.mean(f0)

        # calcular variação do pitch ao longo do tempo:
        pitch_variation = np.std(f0)

        #calcular frequencia mundamental maxima
        maxF0 = np.max(f0)

        #calcular frequência fundamental minima
        minF0 = np.min(f0)

        self.diagnostico['frequencia fundamental'] = f0
        self.diagnostico['pitch_medio'] = medium_pitch
        self.diagnostico['varicao_pitch'] = pitch_variation
        self.diagnostico['frequencia_fundamental_maxima'] = maxF0
        self.diagnostico['frequencia_fundamental_minima'] = minF0

        self.makeF0Plot(y=y,sr=sr)

    #coeficientes cepstrais em frequência mel
    def mfcc(self, audio):
        y, sr = librosa.load(audio)  # Carregar o audio

        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)  # 

        self.diagnostico['mfccs'] = mfccs
    
    def makeF0Plot(self,y,sr):
        times = librosa.times_like(self.diagnostico['frequencia fundamental'], sr=sr)

        D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
        fig, ax = plt.subplots()
        img = librosa.display.specshow(D, x_axis='tempo (s)', y_axis='Frequência (HZ)', ax=ax)
        plt.set(title='Estimativa de Frequência Fundamental (f0)')
        plt.colorbar(img, ax=ax, format="%+2.f dB")
        plt.plot(times, self.diagnostico['frequencia fundamental'], label='f0', color='cyan', linewidth=3)
        plt.legend(loc='upper right')
        plt.savefig('../../Grafico/grafico_de_frequencia_fundamental.png')
        #plt.show()
    
    #intensidade (energia) do sinal de áudio(Loudness)
    def loudness(self, audio):
        y, sr = librosa.load(audio)  # Carregar o audio

        # Calcular a intensidade (RMS)
        rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=512)[0]


        times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=512)

        #================== Plotar a intensidade da fala ==========================
        plt.figure(figsize=(10, 6))
        plt.plot(times, rms, label='Intensidade da Fala (RMS)', color='r')
        plt.xlabel('Tempo (s)')
        plt.ylabel('Intensidade (RMS)')
        plt.title('Intensidade da Fala ao Longo do Tempo')
        plt.legend()
        plt.grid()
        plt.savefig('../../Grafico/grafico_de_Intensidade_da_fala_Energia.png')
        #plt.show()

    def formante(self,audio):
        
        sound = parselmouth.Sound(audio)     # Carregar o arquivo de áudio

        formants = sound.to_formant_burg()

        times = np.linspace(0, sound.get_total_duration(), formants.get_number_of_frames())

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
        plt.savefig('../../Grafico/grafico_de_formantes.png')
        #plt.show()

    def jitterShimmer(self,audio):
        y, sr = librosa.load(audio)  # Carregar o audio

        # Calcular a diferença entre períodos consecutivos
        periods = librosa.effects.split(y, top_db=20)
        diffs = np.diff(periods)
        self.diagnostico['jitter'] =  np.mean(diffs) / np.mean(periods)

        # Calcular a diferença entre amplitudes consecutivas
        amplitudes = np.abs(y)
        diffs = np.diff(amplitudes)
        self.diagnostico['shimmer'] = np.mean(diffs) / np.mean(amplitudes)

    def articulation_rate(self, audio):
        y, sr = librosa.load(audio)  # Carregar o audio

        intervals = librosa.effects.split(y, top_db=20) # dectetar silencio

        total_sounding_duration = sum((end - start) / sr for start, end in intervals)         # Calcular a duração total de fala ativa

        # Contar o número de sílabas/número de picos de energia
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        peaks = librosa.util.peak_pick(onset_env, pre_max=20, post_max=20, pre_avg=50, post_avg=50, delta=0.2, wait=10)

        articulation_rate = len(peaks) / total_sounding_duration
        self.diagnostico['articulation_rate (s)'] = articulation_rate

    def pause_duration_over_time(self, audio):
        y, sr = librosa.load(audio)  # Load audio
        intervals = librosa.effects.split(y, top_db=20)  # Sounding intervals

        total_duration = len(y) / sr
        total_sounding_duration = sum((end - start) / sr for start, end in intervals)
        total_pause_duration = total_duration - total_sounding_duration

        # print(f"Total duration: {total_duration:.2f} sec")
        # print(f"Total sounding duration: {total_sounding_duration:.2f} sec")
        # print(f"Total pause duration: {total_pause_duration:.2f} sec")

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
        # print("\nPause durations over time:")
        # for i, (start_sec, end_sec, dur_sec) in enumerate(pause_durations):
        #     print(f"Pause {i+1}: Start = {start_sec:.2f}s, End = {end_sec:.2f}s, Duration = {dur_sec:.2f}s")

        return pause_durations

    def writeInTheFile(self):
        path = self.filename.split("/")[0].strip() + "/" + self.filename.split("/")[1].strip()
        if not os.path.exists(path=path): 
           os.makedirs(path)

        with open(self.filename, 'a') as file:
            file.write("Resultado do diagnostico da habilidade de comunicação:\n")
            file.write( json.dumps(self.diagnostico))
    
    def fake_show(*args, **kwargs):
            pass  # Não faz nada, apenas substitui plt.show()


    #========================================================================================================
    #Características prosódicas extraídas do áudio:
    #========================================================================================================


    # def prosodyFeatures(self, audio, userName, step):
    #     step = f"{step}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    #     prosody = Prosody()
    #     featuresStatic = prosody.extract_features_file(audio, static=True, plots=True, fmt='dataframe' )
    #     featuresNoStatic = prosody.extract_features_file(audio, static=False, plots=True, fmt='dataframe' )

    #     paths_imagens = []
    #     pasta_destino = os.path.abspath(f"../Grafico/{userName}/prosody")
    #     os.makedirs(pasta_destino, exist_ok=True)

    #     for i, fig_num in enumerate(plt.get_fignums()):
    #         fig = plt.figure(fig_num)
    #         nome_ficheiro = f"prosody_graph_{step}_{i+1}.png"
    #         caminho_completo = os.path.join(pasta_destino, nome_ficheiro)
    #         fig.savefig(caminho_completo, dpi=300, bbox_inches="tight")
    #         paths_imagens.append(caminho_completo)
    #         plt.close(fig)

    #     featuresStatic = pd.DataFrame(featuresStatic)
    #     featuresNoStatic = pd.DataFrame(featuresNoStatic)

    #     document = []
    #     fNoStatic = self.convert_to_json(featuresNoStatic)
    #     featStatic = self.convert_to_json(featuresStatic, static=True)
    #     document.append(featStatic)
    #     document.append(fNoStatic)

    #     self.diagnostico['prosody'] = document

    #     return document, paths_imagens
    def prosodyFeatures(self, audio, userName, step):
        step = f"{step}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        prosody = Prosody()
        featuresStatic = prosody.extract_features_file(audio, static=True, plots=True, fmt='dataframe' )
        featuresNoStatic = prosody.extract_features_file(audio, static=False, plots=True, fmt='dataframe' )

        # Pasta local temporária para gerar imagem
        pasta_temporaria = os.path.abspath(f"../Grafico/{userName}/prosody")
        os.makedirs(pasta_temporaria, exist_ok=True)

        # Lista com os caminhos públicos recebidos do backend
        paths_imagens_backend = []

        for i, fig_num in enumerate(plt.get_fignums()):
            fig = plt.figure(fig_num)
            nome_ficheiro = f"prosody_graph_{step}_{i+1}.png"
            caminho_local = os.path.join(pasta_temporaria, nome_ficheiro)
            fig.savefig(caminho_local, dpi=300, bbox_inches="tight")
            plt.close(fig)

            # Envia para backend
            # caminho_backend = self.enviar_imagem_para_backend(caminho_local, userName, "prosody")
            if caminho_local:
                paths_imagens_backend.append(caminho_local)

        # Processamento dos dados para retorno
        featuresStatic = pd.DataFrame(featuresStatic)
        featuresNoStatic = pd.DataFrame(featuresNoStatic)

        document = []
        fNoStatic = self.convert_to_json(featuresNoStatic)
        featStatic = self.convert_to_json(featuresStatic, static=True)

        #:::::::::::::::::::::::::::::::::::::F0:::::::::::::::::::::::::::::::::::::
        x, fs = sf.read(audio)
        f0, sp, ap = pyworld.wav2world(x, fs)  # Extract F0, spectral envelope, and aperiodicity
        f0 = f0[np.where(f0 > 0)[0]]  # remover valores null

        #::::::::::::::::::::::::::::::::::::Intensidade::::::::::::::::::::::::::::::
        intensidade = self.gerar_json_intensidade(audio)
        

        #::::::::::::::::::::::::::::::::::::Pause Duraction:::::::::::::::::::::::::::::

        pause_durations = self.pause_duration_over_time(audio)
        
        #:::::::::::::::::::::::::::::::::::::Velocidade de Fala::::::::::::::::::::::::::

        metricas,snd = self.analisar_silabas_rapidas_velocidade_da_fala(audio)

        caminho_local = self.plotar_analise_silabas_rapidas(metricas=metricas,snd=snd, pasta_temporaria=pasta_temporaria,step=step)

        if caminho_local:
            paths_imagens_backend.append(caminho_local)

        fNoStatic['F0'] = f0.tolist()
        fNoStatic['PauseDurations'] = pause_durations
        fNoStatic['SpeechRate'] = metricas
        fNoStatic['intensidade'] = intensidade
        
        document.append(featStatic)
        document.append(fNoStatic)
        # document.append(f0)
        self.diagnostico['prosody'] = document

        return document, paths_imagens_backend
    #========================================================================================================
    #Características glotal extraídas do áudio:
    
    # def glottalFeatures(self, audio, userName, step):
    #     step = f"{step}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    #     glottal =  Glottal()
    #     featuresStatic = glottal.extract_features_file(audio, static=True, plots=True, fmt='dataframe' )
    #     featuresNoStatic = glottal.extract_features_file(audio, static=False, plots=True, fmt='dataframe' )

    #     paths_imagens = []
    #     pasta_destino = os.path.abspath(f"../Grafico/{userName}/glottal")
    #     os.makedirs(pasta_destino, exist_ok=True)

    #     for i, fig_num in enumerate(plt.get_fignums()):
    #         fig = plt.figure(fig_num)
    #         nome_ficheiro = f"glottal_graph_{step}_{i+1}.png"
    #         caminho_completo = os.path.join(pasta_destino, nome_ficheiro)
    #         fig.savefig(caminho_completo, dpi=300, bbox_inches="tight")
    #         paths_imagens.append(caminho_completo)
    #         plt.close(fig)

    #     featuresStatic = pd.DataFrame(featuresStatic)
    #     featuresNoStatic = pd.DataFrame(featuresNoStatic)

    #     document = []
    #     fNoStatic = self.convert_to_json(featuresNoStatic)
    #     featStatic = self.convert_to_json(featuresStatic, static=True)
    #     document.append(featStatic)
    #     document.append(fNoStatic)

    #     self.diagnostico['glottal'] = document

    #     return document, paths_imagens

    def glottalFeatures(self, audio, userName, step):
        step = f"{step}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        glottal = Glottal()
        featuresStatic = glottal.extract_features_file(audio, static=True, plots=True, fmt='dataframe' )
        featuresNoStatic = glottal.extract_features_file(audio, static=False, plots=True, fmt='dataframe' )

        # Pasta local temporária para gerar imagem
        pasta_temporaria = os.path.abspath(f"../Grafico/{userName}/glottal")
        os.makedirs(pasta_temporaria, exist_ok=True)

        # Lista com os caminhos públicos recebidos do backend
        paths_imagens_backend = []

        for i, fig_num in enumerate(plt.get_fignums()):
            fig = plt.figure(fig_num)
            nome_ficheiro = f"glottal_graph_{step}_{i+1}.png"
            caminho_local = os.path.join(pasta_temporaria, nome_ficheiro)
            fig.savefig(caminho_local, dpi=300, bbox_inches="tight")
            plt.close(fig)

            # # Envia para backend
            # caminho_backend = self.enviar_imagem_para_backend(caminho_local, userName, "glottal")
            if caminho_local:
                paths_imagens_backend.append(caminho_local)

        # Processamento dos dados para retorno
        featuresStatic = pd.DataFrame(featuresStatic)
        featuresNoStatic = pd.DataFrame(featuresNoStatic)

        document = []
        fNoStatic = self.convert_to_json(featuresNoStatic)
        featStatic = self.convert_to_json(featuresStatic, static=True)

        document.append(featStatic)
        document.append(fNoStatic)
        self.diagnostico['glottal'] = document

        return document, paths_imagens_backend

    #========================================================================================================
    # Características de fonacão extraídas do áudio:
    # def phonationFeatures(self, audio, userName,step):
    #     step = f"{step}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    #     phonation =  Phonation()
    #     featuresStatic = phonation.extract_features_file(audio, static=True, plots=True, fmt='dataframe' )
    #     featuresNoStatic = phonation.extract_features_file(audio, static=False, plots=True, fmt='dataframe' )

    #     paths_imagens = []
    #     pasta_destino = os.path.abspath(f"../Grafico/{userName}/phonation")
    #     os.makedirs(pasta_destino, exist_ok=True)

    #     for i, fig_num in enumerate(plt.get_fignums()):
    #         fig = plt.figure(fig_num)
    #         nome_ficheiro = f"phonation_graph_{step}_{i+1}.png"
    #         caminho_completo = os.path.join(pasta_destino, nome_ficheiro)
    #         fig.savefig(caminho_completo, dpi=300, bbox_inches="tight")
    #         paths_imagens.append(caminho_completo)
    #         plt.close(fig)

    #     featuresStatic = pd.DataFrame(featuresStatic)
    #     featuresNoStatic = pd.DataFrame(featuresNoStatic)

    #     document = []
    #     fNoStatic = self.convert_to_json(featuresNoStatic)
    #     featStatic = self.convert_to_json(featuresStatic, static=True)
    #     document.append(featStatic)
    #     document.append(fNoStatic)

    #     self.diagnostico['phonation'] = document

    #     return document, paths_imagens
    
    def phonationFeatures(self, audio, userName, step):
        step = f"{step}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        phonation =  Phonation()
        featuresStatic = phonation.extract_features_file(audio, static=True, plots=True, fmt='dataframe' )
        featuresNoStatic = phonation.extract_features_file(audio, static=False, plots=True, fmt='dataframe' )

        # Pasta local temporária para gerar imagem
        pasta_temporaria = os.path.abspath(f"../Grafico/{userName}/phonation")
        os.makedirs(pasta_temporaria, exist_ok=True)

        # Lista com os caminhos públicos recebidos do backend
        paths_imagens_backend = []

        for i, fig_num in enumerate(plt.get_fignums()):
            fig = plt.figure(fig_num)
            nome_ficheiro = f"phonation_graph_{step}_{i+1}.png"
            caminho_local = os.path.join(pasta_temporaria, nome_ficheiro)
            fig.savefig(caminho_local, dpi=300, bbox_inches="tight")
            plt.close(fig)

            # Envia para backend
            # caminho_backend = self.enviar_imagem_para_backend(caminho_local, userName, "phonation")
            if caminho_local:
                paths_imagens_backend.append(caminho_local)
        
         
        # Processamento dos dados para retorno
        featuresStatic = pd.DataFrame(featuresStatic)
        featuresNoStatic = pd.DataFrame(featuresNoStatic)


        document = []
        fNoStatic = self.convert_to_json(featuresNoStatic)
        featStatic = self.convert_to_json(featuresStatic, static=True)
        
        #############################################
        # F0 
        #############################################
        # Extração de F0 ao longo do tempo
        x, fs = sf.read(audio)
        f0, sp, ap = pyworld.wav2world(x, fs)  # Extract F0, spectral envelope, and aperiodicity
        f0 = f0[np.where(f0 > 0)[0]]  # remover valores null


        ###################
        # TEMPO MAXIMO DE FONAÇÃO
        ###################

        TMF = self.detectar_tmf_auto(audio)

        #######################
        # Intensidade
        #######################
        # intensidade = self.gerar_json_intensidade(audio)

        featStatic['TMF'] = TMF
        # fNoStatic['intensidade'] = intensidade
        fNoStatic['F0'] = f0.tolist()

        document.append(featStatic)
        document.append(fNoStatic)
        self.diagnostico['phonation'] = document

        return document, paths_imagens_backend
        

    #========================================================================================================
    #Características de articulação extraídas do áudio:

    # def articulationFeatures(self, audio, userName,step):
    #     step = f"{step}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    #     articulation = Articulation()
    #     print("Articulation features extraction started, please wait...", audio)
    #     featuresStatic = articulation.extract_features_file(audio, static=True, plots=True, fmt='dataframe')
    #     featuresNoStatic = articulation.extract_features_file(audio, static=False, plots=True, fmt='dataframe')

    #     paths_imagens = []
    #     pasta_destino = os.path.abspath(f"../Grafico/{userName}/articulation")
    #     os.makedirs(pasta_destino, exist_ok=True)

    #     # pasta_destino = os.path.abspath(f"./static/grafico/{userName}/articulation")
    #     # pasta_destino = os.path.abspath(f"C:/Users/Adalb/Desktop/startWthReact/backend/static/grafico/{userName}/articulation")
    #     # os.makedirs(pasta_destino, exist_ok=True)

    #     # caminho = "C:/meu_sistema/temp/articulation_graph_123.png"
    #     # caminho_backend = self.enviar_imagem_para_backend(caminho, "Adalberto_Junior", "articulation")
    #     # print("Imagem disponível em:", caminho_backend)


    #     for i, fig_num in enumerate(plt.get_fignums()):
    #         fig = plt.figure(fig_num)
    #         nome_ficheiro = f"articulation_graph_{step}_{i+1}.png"
    #         caminho_completo = os.path.join(pasta_destino, nome_ficheiro)
    #         fig.savefig(caminho_completo, dpi=300, bbox_inches="tight")
    #         paths_imagens.append(caminho_completo)
    #         plt.close(fig)

    #     featuresStatic = pd.DataFrame(featuresStatic)
    #     featuresNoStatic = pd.DataFrame(featuresNoStatic)

    #     document = []
    #     fNoStatic = self.convert_to_json(featuresNoStatic)
    #     featStatic = self.convert_to_json(featuresStatic, static=True)
    #     document.append(featStatic)
    #     document.append(fNoStatic)

    #     self.diagnostico['articulation'] = document

    #     return document, paths_imagens
    
    def articulationFeatures(self, audio, userName, step):
        step = f"{step}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        articulation = Articulation()

        featuresStatic = articulation.extract_features_file(audio, static=True, plots=True, fmt='dataframe')
        featuresNoStatic = articulation.extract_features_file(audio, static=False, plots=True, fmt='dataframe')

        # Pasta local temporária para gerar imagem
        pasta_temporaria = os.path.abspath(f"../Grafico/{userName}/articulation")
        os.makedirs(pasta_temporaria, exist_ok=True)

        
        paths_imagens_to_backend = []  # Lista para os caminhos locais

        for i, fig_num in enumerate(plt.get_fignums()):
            fig = plt.figure(fig_num)
            nome_ficheiro = f"articulation_graph_{step}_{i+1}.png"
            caminho_local = os.path.join(pasta_temporaria, nome_ficheiro)
            fig.savefig(caminho_local, dpi=300, bbox_inches="tight")
            plt.close(fig)

            
            if caminho_local:
                paths_imagens_to_backend.append(caminho_local)

        # Processamento dos dados para retorno
        featuresStatic = pd.DataFrame(featuresStatic)
        featuresNoStatic = pd.DataFrame(featuresNoStatic)

        document = []
        fNoStatic = self.convert_to_json(featuresNoStatic)
        featStatic = self.convert_to_json(featuresStatic, static=True)

        document.append(featStatic)
        document.append(fNoStatic)
        self.diagnostico['articulation'] = document

        return document, paths_imagens_to_backend

       
        

    # def phonologicalFeatures (self, audio):

    #     #plt.show = self.fake_show
    #     step = self.returnAudioNameSplit(audio)
    #     phonological =  Phonological()
    #     featuresStatic = phonological.extract_features_file(audio, static=True, plots=True, fmt='dataframe' )
    #     featuresNoStatic = phonological.extract_features_file(audio, static=False, plots=True, fmt='dataframe' )

    #     for i, fig_num in enumerate(plt.get_fignums()):
    #         fig = plt.figure(fig_num)
    #         fig.savefig(f"../Grafico/phonological_graph_{step}_{i+1}.png", dpi=300, bbox_inches="tight")
    #         plt.close(fig)

    #     featuresStatic = pd.DataFrame(featuresStatic)
    #     featuresNoStatic = pd.DataFrame(featuresNoStatic)

    #     document = []
    #     fNoStatic = self.convert_to_json(featuresNoStatic)
    #     featStatic = self.convert_to_json(featuresStatic,static = True)
    #     document.append(featStatic)
    #     document.append(fNoStatic)

    #     #fNoStatic = featuresNoStatic.to_dict(orient='records')
    #     #featStatic = featuresStatic.to_dict(orient='records')
    #     self.diagnostico['phonological'] = document
        
    #     return document
    
    # def phonologicalFeatures(self, audio, userName, step):
    #     step = f"{step}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    #     phonological =  Phonological()
    #     featuresStatic = phonological.extract_features_file(audio, static=True, plots=True, fmt='dataframe' )
    #     featuresNoStatic = phonological.extract_features_file(audio, static=False, plots=True, fmt='dataframe' )

    #     paths_imagens = []
    #     pasta_destino = os.path.abspath(f"../Grafico/{userName}/phonological")
    #     os.makedirs(pasta_destino, exist_ok=True)

    #     for i, fig_num in enumerate(plt.get_fignums()):
    #         fig = plt.figure(fig_num)
    #         nome_ficheiro = f"phonological_graph_{step}_{i+1}.png"
    #         caminho_completo = os.path.join(pasta_destino, nome_ficheiro)
    #         fig.savefig(caminho_completo, dpi=300, bbox_inches="tight")
    #         paths_imagens.append(caminho_completo)
    #         plt.close(fig)

    #     featuresStatic = pd.DataFrame(featuresStatic)
    #     featuresNoStatic = pd.DataFrame(featuresNoStatic)

    #     document = []
    #     fNoStatic = self.convert_to_json(featuresNoStatic)
    #     featStatic = self.convert_to_json(featuresStatic, static=True)
    #     document.append(featStatic)
    #     document.append(fNoStatic)

    #     self.diagnostico['phonological'] = document

    #     return document, paths_imagens
    
    def phonologicalFeatures(self, audio, userName, step):
        step = f"{step}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        phonological =  Phonological()
        featuresStatic = phonological.extract_features_file(audio, static=True, plots=True, fmt='dataframe' )
        featuresNoStatic = phonological.extract_features_file(audio, static=False, plots=True, fmt='dataframe' )

        # Pasta local temporária para gerar imagem
        pasta_temporaria = os.path.abspath(f"../Grafico/{userName}/phonological")
        os.makedirs(pasta_temporaria, exist_ok=True)

        # Lista com os caminhos públicos recebidos do backend
        paths_imagens_backend = []

        for i, fig_num in enumerate(plt.get_fignums()):
            fig = plt.figure(fig_num)
            nome_ficheiro = f"phonological_graph_{step}_{i+1}.png"
            caminho_local = os.path.join(pasta_temporaria, nome_ficheiro)
            fig.savefig(caminho_local, dpi=300, bbox_inches="tight")
            plt.close(fig)

            # Envia para backend
            # caminho_backend = self.enviar_imagem_para_backend(caminho_local, userName, "phonological")
            if caminho_local:
                paths_imagens_backend.append(caminho_local)

        # Processamento dos dados para retorno
        featuresStatic = pd.DataFrame(featuresStatic)
        featuresNoStatic = pd.DataFrame(featuresNoStatic)

        document = []
        fNoStatic = self.convert_to_json(featuresNoStatic)
        featStatic = self.convert_to_json(featuresStatic, static=True)

        document.append(featStatic)
        document.append(fNoStatic)
        self.diagnostico['phonological'] = document

        return document, paths_imagens_backend

    
    # def replearningFeatures (self, audio, model = 'CAE'):
    #     #plt.show = self.fake_show
    #     step = self.returnAudioNameSplit(audio)

    #     replearning = RepLearning(model)
    #     featuresStatic = replearning.extract_features_file(audio, static=True,plots=True, fmt ='dataframe') #Variação no tempo
    #     featuresNoStatic = replearning.extract_features_file(audio, static=False, plots=True, fmt ='dataframe')

    #     for i, fig_num in enumerate(plt.get_fignums()):
    #         fig = plt.figure(fig_num)
    #         fig.savefig(f"../Grafico/replearning_graph_{step}_{i+1}.png", dpi=300, bbox_inches="tight")
    #         plt.close(fig)

    #     featuresStatic = pd.DataFrame(featuresStatic)
    #     featuresNoStatic = pd.DataFrame(featuresNoStatic)

    #     document = []
    #     fNoStatic = self.convert_to_json(featuresNoStatic)
    #     featStatic = self.convert_to_json(featuresStatic,static = True)
    #     document.append(featStatic)
    #     document.append(fNoStatic)

    #     #fNoStatic = featuresNoStatic.to_dict(orient='records')
    #     #featStatic = featuresStatic.to_dict(orient='records')
    #     self.diagnostico['replearning'] = document
        
    #     return document

    # def replearningFeatures(self, audio, userName,step, model = 'CAE' ):
    #     step = f"{step}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    #     replearning = RepLearning(model)
    #     featuresStatic = replearning.extract_features_file(audio, static=True,plots=True, fmt ='dataframe') #Variação no tempo
    #     featuresNoStatic = replearning.extract_features_file(audio, static=False, plots=True, fmt ='dataframe')

    #     paths_imagens = []
    #     pasta_destino = os.path.abspath(f"../Grafico/{userName}/replearning")
    #     os.makedirs(pasta_destino, exist_ok=True)

    #     for i, fig_num in enumerate(plt.get_fignums()):
    #         fig = plt.figure(fig_num)
    #         nome_ficheiro = f"replearning_graph_{step}_{i+1}.png"
    #         caminho_completo = os.path.join(pasta_destino, nome_ficheiro)
    #         fig.savefig(caminho_completo, dpi=300, bbox_inches="tight")
    #         paths_imagens.append(caminho_completo)
    #         plt.close(fig)

    #     featuresStatic = pd.DataFrame(featuresStatic)
    #     featuresNoStatic = pd.DataFrame(featuresNoStatic)

    #     document = []
    #     fNoStatic = self.convert_to_json(featuresNoStatic)
    #     featStatic = self.convert_to_json(featuresStatic, static=True)
    #     document.append(featStatic)
    #     document.append(fNoStatic)

    #     self.diagnostico['replearning'] = document

    #     return document, paths_imagens
    
    def replearningFeatures(self, audio, userName,step, model = 'CAE' ):
        step = f"{step}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        replearning = RepLearning(model)
        featuresStatic = replearning.extract_features_file(audio, static=True,plots=True, fmt ='dataframe') #Variação no tempo
        featuresNoStatic = replearning.extract_features_file(audio, static=False, plots=True, fmt ='dataframe')

        # Pasta local temporária para gerar imagem
        pasta_temporaria = os.path.abspath(f"../Grafico/{userName}/replearning")
        os.makedirs(pasta_temporaria, exist_ok=True)

        # Lista com os caminhos públicos recebidos do backend
        paths_imagens_backend = []

        for i, fig_num in enumerate(plt.get_fignums()):
            fig = plt.figure(fig_num)
            nome_ficheiro = f"replearning_graph_{step}_{i+1}.png"
            caminho_local = os.path.join(pasta_temporaria, nome_ficheiro)
            fig.savefig(caminho_local, dpi=300, bbox_inches="tight")
            plt.close(fig)

            # Envia para backend
            # caminho_backend = self.enviar_imagem_para_backend(caminho_local, userName, "replearning")
            if caminho_local:
                paths_imagens_backend.append(caminho_local)

        # Processamento dos dados para retorno
        featuresStatic = pd.DataFrame(featuresStatic)
        featuresNoStatic = pd.DataFrame(featuresNoStatic)

        document = []
        fNoStatic = self.convert_to_json(featuresNoStatic)
        featStatic = self.convert_to_json(featuresStatic, static=True)

        document.append(featStatic)
        document.append(fNoStatic)
        self.diagnostico['replearning'] = document

        return document, paths_imagens_backend
    

    def extrair_intensidade(self, audio_path):
        snd = parselmouth.Sound(audio_path)
        intensity = snd.to_intensity()
        # tempos = intensity.xs()
        # valores = [intensity.get_value(time=t) or 0 for t in tempos]

        # print("Intensidade2: ", intensity)
        # return tempos, valores
        return intensity
    

    def detectar_tmf_auto(self, audio):
        
        intensity = self.extrair_intensidade(audio)

        # Calcula a média da intensidade (ignorando valores nulos)
        valores = [intensity.get_value(time=t) for t in intensity.xs()]
        valores_validos = [v for v in valores if v is not None]
        media_db = sum(valores_validos) / len(valores_validos)

        # Define o limiar como 60% da média (ajustável)
        threshold_db = media_db * 0.6

        start_time = None
        end_time = None

        for t in intensity.xs():
            valor = intensity.get_value(time=t)
            if valor and valor > threshold_db:
                if start_time is None:
                    start_time = t
                end_time = t

        if start_time and end_time:
            tmf = end_time - start_time
            return tmf
        else:
            print("Não foi possível detectar fonação.")
            return None
        

    def gerar_json_intensidade(self, audio):
        """
        Extrai a intensidade vocal de um arquivo .wav e salva como JSON.

        Parâmetros:
        - caminho_audio: str, caminho para o arquivo .wav

        Retorna:
        - Lista de dicionários com 'time' e 'db'
        """

        intensidade = self.extrair_intensidade(audio)

        tempos = intensidade.xs()
        valores_db = [intensidade.get_value(time=t) for t in tempos]

        print("Tempos: ",len(tempos))
        print("valores : ",len(valores_db))

        dados = [
            {"time": float(t), "db": float(db)}
            for t, db in zip(tempos, valores_db)
            if db is not None and db > 0
        ]
        return dados
    
    
    def analisar_silabas_rapidas_velocidade_da_fala(self, audio):
        snd = parselmouth.Sound(audio)

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
        #TODO: PENSAR NA FORMA DE APRESENTAR AS LABELS DAS SÍLABAS
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
            "time": time_intensity.tolist(),      # ✅ corrigido
            "intensity": intensity_values.tolist(), # ✅ corrigido
            "pitch": pitch_interp.tolist()
        }


        return metricas, snd
    

    def plotar_analise_silabas_rapidas(self, metricas, snd, pasta_temporaria,step):
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
        nome_ficheiro = f"intensidade_chart_{step}.png"
        caminho_local = os.path.join(pasta_temporaria, nome_ficheiro)
        fig.savefig(caminho_local, dpi=300, bbox_inches="tight")
        plt.close(fig)

        return caminho_local
    
    
    def getResult(self):
        #print(self.diagnostico)
        return json.dumps(self.diagnostico)
    
    def convert_to_json(self,df, static = False):
        documento = {}
        i = -1
        # Iterar pelas linhas do DataFrame
        for _, linha in df.iterrows():
            i +=1
            for coluna in df.columns:  # Iterar pelas colunas
                if static == True:
                    if str(linha[coluna]) != '0.0':
                        documento[coluna] = linha[coluna]
                else:
                    if i == 0:
                        if str(linha[coluna]) != '0.0':
                            documento[coluna] = [linha[coluna]]
                        else:
                            documento[coluna] = []
                    else:
                        if str(linha[coluna]) != '0.0':
                            documento[coluna].append(linha[coluna])  # Adicionar chave (coluna) e valor

        return documento

    def returnAudioNameSplit (self, audio):
        name = audio.split("/")[-1].strip()
        return name.replace(".wav","")


    def enviar_imagem_para_backend(self, caminho_imagem, userName, subpasta):
        url_backend = "http://localhost:5000/casa_viva/home/upload-imagem"  # ou IP real do backend
        try:
            with open(caminho_imagem, "rb") as f:
                files = {"file": f}
                data = {
                    "userName": userName,
                    "subpasta": subpasta  # Ex: articulation, prosody...
                }
                response = requests.post(url_backend, files=files, data=data)
                if response.status_code == 200:
                    print("Imagem enviada com sucesso!")
                    return response.json()["path"]
                else:
                    print("Erro ao enviar:", response.text)
        except Exception as e:
            print("Erro:", e)
        return None
    

    # def enviar_dados_para_backend(self, caminho_imagem, userName, subpasta):
    #     url_backend = "http://localhost:5000/casa_viva/home/upload-imagem"
    #     try:
    #         with open(caminho_imagem, "rb") as f:
    #             imagem_bytes = f.read()
    #         data = {
    #             "userName": userName,
    #             "subpasta": subpasta,
    #             "imagem": imagem_bytes.decode("latin1")  # or base64 encode for safety
    #         }
    #         headers = {'Content-Type': 'application/json'}
    #         response = requests.post(url_backend, data=json.dumps(data), headers=headers)
    #         if response.status_code == 200:
    #             print("Dados enviados com sucesso!")
    #             return response.json()["path"]
    #         else:
    #             print("Erro ao enviar:", response.text)
    #     except Exception as e:
    #         print("Erro:", e)
    #     return None




