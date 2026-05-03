import pyaudio
import wave
import threading
import speech_recognition as sr

class Recorder:
    def __init__(self, output_filename="output.wav"):
        self.output_filename = output_filename
        self.is_recording = False
        self.stop_recording = False
    
    def start_recording(self):
        self.is_recording = True
        self.stop_recording = False
        self.audio = pyaudio.PyAudio()
        
        self.stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        self.frames = []

        def record():
            while self.is_recording and not self.stop_recording:
                data = self.stream.read(1024)
                self.frames.append(data)

            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()

            wave_file = wave.open(self.output_filename, 'wb')
            wave_file.setnchannels(1)
            wave_file.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wave_file.setframerate(44100)
            wave_file.writeframes(b''.join(self.frames))
            wave_file.close()

        self.recording_thread = threading.Thread(target=record)
        self.recording_thread.start()

    def stop_recording(self):
        self.is_recording = False
        self.recording_thread.join()

    def stop_recording_on_command(self):
        self.stop_recording = True

    def listen_for_keyword(self, keyword="terminei"):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            recognizer.adjust_for_ambient_noise(source)

        while not self.stop_recording:
            with mic as source:
                audio = recognizer.listen(source)
                try:
                    transcript = recognizer.recognize_google(audio, language='pt-PT')
                    print(f"Ouvi: {transcript}")
                    if keyword in transcript.lower():
                        self.stop_recording_on_command()
                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    print(f"Erro no serviço de reconhecimento de fala: {e}")
                    break

# Uso no programa principal:
recorder = Recorder()

# Iniciar gravação
recorder.start_recording()

# Iniciar thread para escutar palavra-chave
keyword_thread = threading.Thread(target=recorder.listen_for_keyword)
keyword_thread.start()

# Parar a gravação manualmente depois de um tempo (simulação de decisão do programa principal)
import time
time.sleep(10)
recorder.stop_recording()

# Esperar pela thread de escuta de palavra-chave
keyword_thread.join()
#
# ====================================================================================================
# ====================================================================================================
# ====================================================================================================


import pyaudio
import wave
import threading
import speech_recognition as sr

class RecorderWithKeyword:
    def __init__(self, output_filename="output_keyword.wav", keyword="terminei"):
        self.output_filename = output_filename
        self.keyword = keyword.lower()
        self.is_recording = False
        self.frames = []
        self.stop_signal = threading.Event()  # Evento para sinalizar parada

    def start_recording(self):
        self.is_recording = True
        self.audio = pyaudio.PyAudio()
        
        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=44100,
                                      input=True,
                                      frames_per_buffer=1024)
        
        def record():
            while not self.stop_signal.is_set():
                data = self.stream.read(1024)
                self.frames.append(data)
            
            # Finaliza a gravação
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()
            
            wave_file = wave.open(self.output_filename, 'wb')
            wave_file.setnchannels(1)
            wave_file.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wave_file.setframerate(44100)
            wave_file.writeframes(b''.join(self.frames))
            wave_file.close()
        
        def listen_for_keyword():
            recognizer = sr.Recognizer()
            mic = sr.Microphone()

            with mic as source:
                recognizer.adjust_for_ambient_noise(source)  # Ajusta para ruído ambiente

            while not self.stop_signal.is_set():
                with mic as source:
                    print("Aguardando palavra-chave...")
                    audio_data = recognizer.listen(source, phrase_time_limit=2)
                try:
                    transcript = recognizer.recognize_google(audio_data, language='pt-PT')
                    print(f"Você disse: {transcript}")
                    if self.keyword in transcript.lower():
                        print("Palavra-chave detectada! Parando gravação.")
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

    def stop_recording(self):
        self.stop_signal.set()
        self.recording_thread.join()
        self.keyword_thread.join()


# programa_principal_2.py

# Cria uma instância do RecorderWithKeyword
recorder = RecorderWithKeyword("audio_palavra_chave.wav", keyword="terminei")

# Inicia a gravação
recorder.start_recording()
print("Gravação iniciada. Diga 'terminei' para parar.")

# Aguarda a gravação terminar automaticamente
recorder.recording_thread.join()
print("Gravação encerrada após detectar a palavra-chave.")
