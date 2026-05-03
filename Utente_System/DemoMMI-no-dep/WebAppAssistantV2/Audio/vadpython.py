import pyaudio
import webrtcvad
import os
import wave
import time

# Configurações de áudio
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK_DURATION_MS = 30
CHUNK_SIZE = int(RATE * CHUNK_DURATION_MS / 1000)
ti = time.time()

# Inicializar PyAudio e WebRTC VAD
audio = pyaudio.PyAudio()
vad = webrtcvad.Vad()
vad.set_mode(3)  # 0: menos agressivo, 3: mais agressivo

# Função para capturar áudio
def get_audio_stream():
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK_SIZE)
    return stream

# Função para processar áudio e detectar voz
def detect_voice():
    stream = get_audio_stream()
    frames = []
    start_time = 0
    start = 0
    
    print("Iniciando detecção de voz. Pressione Ctrl+C para parar.")
    try:
        while start != 77:
           
            audio_chunk = stream.read(CHUNK_SIZE, exception_on_overflow=False)
           
           # Certifique-se de que o frame é do tipo bytes
            if isinstance(audio_chunk, bytes):
                frames.append(audio_chunk)
                is_speech = vad.is_speech(audio_chunk, RATE)
                if is_speech:
                    start = 0
                    print("Voz detectada!")
                else:
                    if start == 0:
                        start_time = time.time()
                        start +=1 
                        print(f"Start: {start}")
                    print("Silêncio...")
                    #stop_time = time.time()
                    if (time.time() - start_time) > 5:
                        print("Já passaram {seg:.0f} em silencio".format(seg = (time.time() - start_time) ))
                        start = 77
                    
            else:
                print("Frame inválido.")
    except KeyboardInterrupt:
        print("Detecção de voz interrompida.")
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()
        saveAudio(frames)

def saveAudio(frames):
        filename = "text.wav"
        path = "../Audio/"
        if not os.path.exists(path):
            os.makedirs(path)
        path = path + filename
        wf = wave.open(path, "wb")
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

# Iniciar detecção de voz
detect_voice()
