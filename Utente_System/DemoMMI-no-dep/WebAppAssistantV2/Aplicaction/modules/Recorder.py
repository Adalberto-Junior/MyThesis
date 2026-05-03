#====================================================================================================
# File Name : Recorder.py
# Autor : Adalberto Junior
# Date : 2025-02-21
# Version : 1.0
# Description : This module is responsible for recording the user's voice. It uses the pyaudio library to record the audio and save it in a .wav file. 
# 
# ====================================================================================================
# ====================================================================================================
# ====================================================================================================
# ====================================================================================================

import pyaudio
import wave
import os
import time
import threading
import asyncio
import webrtcvad
import speech_recognition as sr

class Recorder:
    #filename = "output.wav"

    #Constructor of the class
    def __init__(self, path, filename="output.wav", seconds = 30,keyword="terminei"):
        #self.filename = filename
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.RATE2 = 16000
        self.RECORD_SECONDS = seconds
        self.WAVE_OUTPUT_FILENAME = filename
        self.audioPath = os.path.join(path,  self.WAVE_OUTPUT_FILENAME.split('.')[0])
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.is_recording = False       #Variable to control the recording
        self.keyword = keyword.lower()
        self.stop_signal = threading.Event()  # Evento para sinalizar parada
        self.CHUNK_DURATION_MS = 30
        self.CHUNK_SIZE = int(self.RATE2 * self.CHUNK_DURATION_MS / 1000)
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(3)
    

    
    #Method to configure the audio
    def configAudio(self):
        self.stream = self.audio.open(format=self.FORMAT,
                    channels=self.CHANNELS,
                    rate=self.RATE,
                    input=True,
                    frames_per_buffer=self.CHUNK)
    
    #Method to configure the audio
    def configAudio_v2(self):
        self.stream = self.audio.open(format=self.FORMAT,
                    channels=self.CHANNELS,
                    rate=self.RATE2,
                    input=True,
                    frames_per_buffer=self.CHUNK_SIZE)
    
    #Method to finish the audio and close the stream
    def finishAudio(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
    
    """ Method to save the audio in a file .wav """
    def saveAudio(self):

        if not os.path.exists(self.audioPath):
            os.makedirs(self.audioPath)

        self.audioPath = os.path.join(self.audioPath, self.WAVE_OUTPUT_FILENAME)
        wf = wave.open(self.audioPath, "wb")
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()
    
    """ Method to save the audio in a file .wav v2 """
    def saveAudio_v2(self):
        
        if not os.path.exists(self.audioPath):
            os.makedirs(self.audioPath)

        self.audioPath = os.path.join(self.audioPath, self.WAVE_OUTPUT_FILENAME.split('.')[0] + ".wav")
        wf = wave.open(self.audioPath, "wb")
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.RATE2)
        wf.writeframes(b''.join(self.frames))
        wf.close()
       
    """ Method to record the audio """
    def record(self):
        self.configAudio()
        print("* recording")
        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            data = self.stream.read(self.CHUNK)
            self.frames.append(data)
        print("* done recording")
        self.finishAudio()
        self.saveAudio()
        return self.WAVE_OUTPUT_FILENAME
    
    #Method to record audio and make vad:
    def record_vad(self):
        try:
            self.configAudio_v2()
            start_time = 0
            start = 0
            print("* recording")
            while start != 77:
                audio_chunk = self.stream.read(self.CHUNK_SIZE, exception_on_overflow=False)
            
                if isinstance(audio_chunk, bytes):  # Certifica que o frame é do tipo bytes
                    self.frames.append(audio_chunk)
                    is_speech = self.vad.is_speech(audio_chunk, self.RATE2)
                    if is_speech:
                        start = 0
                    else:
                        if start == 0:
                            start_time = time.time()
                            start = 1 
                        #stop_time = time.time()
                        if (time.time() - start_time) > 5:
                            print("Já se passaram {seg:.0f} segundos em silencio".format(seg = (time.time() - start_time) ))
                            start = 77
                            print("* done recording")                     
                else:
                    print("Frame inválido.")
        except KeyboardInterrupt:
            print("Detecção de voz interrompida.")
        finally:
            self.finishAudio()
            self.saveAudio_v2()
    
    #Method to start the recording in a thread
    def start_recording(self):
        self.is_recording = True
        
        self.configAudio()

        def record():
            while self.is_recording:
                data = self.stream.read(self.CHUNK)
                self.frames.append(data)

            self.finishAudio()
            self.saveAudio()

        self.recording_thread = threading.Thread(target=record)
        self.recording_thread.start()
    
    def start_recording_Key(self):
        self.is_recording = True
        self.configAudio()
        
        def record():
            print("* recording")
            while not self.stop_signal.is_set():
                data = self.stream.read(self.CHUNK)
                self.frames.append(data)

            self.finishAudio()
            self.saveAudio()
            print("* done recording")
        
        def listen_for_keyword():
            recognizer = sr.Recognizer()
            mic = sr.Microphone()

            with mic as source:
                recognizer.adjust_for_ambient_noise(source)  # Ajusta para ruído ambiente

            while not self.stop_signal.is_set():
                with mic as source:
                    #print("Aguardando palavra-chave...")
                    audio_data = recognizer.listen(source, phrase_time_limit=2)
                try:
                    transcript = recognizer.recognize_google(audio_data, language='pt-PT')
                    #print(f"Você disse: {transcript}")
                    if self.keyword in transcript.lower():
                        print("Palavra-chave detectada! Parando gravação...")
                        self.stop_signal.set()
                except sr.UnknownValueError:
                    # Não foi possível entender o áudio
                    pass
                except sr.RequestError as e:
                    print(f"Erro no serviço de reconhecimento de fala: {e}")
                    break

        # Inicia as threads
        self.recording_thread = threading.Thread(target=record)
        self.keyword_thread = threading.Thread(target=listen_for_keyword)
        self.recording_thread.start()
        self.keyword_thread.start()
    
    
    
    #Method to stop the recording and join the thread
    def stop_recording(self):
        self.is_recording = False
        self.recording_thread.join()
    
    def stop_recording_key(self):
        self.stop_signal.set()
        self.recording_thread.join()
        self.keyword_thread.join()

    #Method to delete the audio file
    def deleteAudio(self):
        os.remove(self.audioPath)
        print("File Removed!")
    
#====================================================================================================
#  File Name : Recorder.py

        