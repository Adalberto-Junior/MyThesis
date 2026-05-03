# Autor: Adalberto Júnior
# Data: 2025-01-28
# Descrição: Módulo para gravação de áudio
# -*- coding: utf-8 -*-
""""
import wave
import sys
import pyaudio
import asyncio
import websocket
import threading
"""

"""""
# Endereço do servidor WebSocket
host = "localhost"
mmiCli_Out_add = f"ws://{host}:8005"

# Função de manipulação de mensagens recebidas
def im1_message_handler(ws, message):
    print(f"Mensagem recebida: {message}")

def socket_open_handler(ws):
    print("---------------openSocketHandler---------------")
    if ws.sock and ws.sock.connected:
        print("Conexão aberta e pronta para comunicação.")

def on_error(ws, error):
    print(f"Erro no WebSocket: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"Conexão fechada: {close_msg}, código {close_status_code}")

def open_socket():
    websocket.enableTrace(True)  # Habilita logs de debug

    ws = websocket.WebSocketApp(
        mmiCli_Out_add,
        on_message=im1_message_handler,
        on_open=socket_open_handler,
        on_error=on_error,
        on_close=on_close,
    )

    # Executa WebSocket no modo contínuo dentro de uma thread
    thread = threading.Thread(target=ws.run_forever)
    thread.daemon = True  # Permite que a thread pare quando o programa encerrar
    thread.start()

    while True:  # Mantém o programa rodando até ser interrompido
        try:
            pass
        except KeyboardInterrupt:
            print("Encerrando cliente WebSocket...")
            break


def main ():

    # Configuração do dispositivo de áudio
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    frames_per_buffer=1024)

    # Gravação de áudio
    print("Gravando...")
    frames = []
    for i in range(0, int(44100 / 1024 * 5)):
        data = stream.read(1024)
        frames.append(data)

    # Finaliza a gravação
    print("Gravação finalizada.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Salva o arquivo de áudio
    wf = wave.open("output.wav", "wb")
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(44100)
    wf.writeframes(b''.join(frames))
    wf.close()


if __name__ == "__main__":
    #host = "localhost"
    #uri = f"wss://{host}:8005/IM/USER1/APP"
    #asyncio.run(mmi_client_socket(uri))
    open_socket()
    #main()
"""


import asyncio
import websockets
import wave
import sys
import pyaudio

global finisRecording
finisRecording = False
"""""
async def connect():
    uri = "ws://localhost:8005"
    global finisRecording 
    
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Conectado ao servidor WebSocket!")

            # Enviar mensagem para o servidor
            await websocket.send("Olá, servidor!")

            # Receber resposta
            response = await websocket.recv()
            print(f"📩 Mensagem recebida do servidor: {response}")

            if response == "Gravar":
                finisRecording = False
                #recordAudio(websocket)
                stream, p = configAudio()
                print("Gravando...")
                await websocket.send("Gravando...")
                frames = []
                for i in range(0, int(44100 / 1024)):
                    data = stream.read(1024)
                    frames.append(data)
                    
                    if finisRecording:
                        break
                
                #await websocket.send("Gravação finalizada.")
                #finisRecording = True

            # Manter a conexão aberta
            while True:
                await asyncio.sleep(1)

    except Exception as e:
        print(f"❌ Erro na conexão: {e}")


def configAudio():
    # Configuração do dispositivo de áudio
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    frames_per_buffer=1024)
    return stream, p

def finishAudio(stream,p):
    stream.stop_stream()
    stream.close()
    p.terminate()

def saveAudio(frames):
    # Salva o arquivo de áudio
    wf = wave.open("output.wav", "wb")
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(44100)
    wf.writeframes(b''.join(frames))
    wf.close()


async def recordAudio (websocket):
    global finisRecording

    # Configuração do dispositivo de áudio
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    frames_per_buffer=1024)

    # Gravação de áudio
    print("Gravando...")
    websocket.send("Gravando...")
    frames = []
    for i in range(0, int(44100 / 1024 )):
        data = stream.read(1024)
        frames.append(data)
        if finisRecording:
            break

    # Finaliza a gravação
    print("Gravação finalizada.")
    websocket.send("Gravação finalizada.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Salva o arquivo de áudio
    wf = wave.open("output.wav", "wb")
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(44100)
    wf.writeframes(b''.join(frames))
    wf.close()

"""

global recording

async def recordAudio(stop_event,websocket):
    global recording
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    fs = 44100
    filename = "output.wav"
    
    p = pyaudio.PyAudio()

    print("Iniciando a gravação...")
    await websocket.send("Gravando...")
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []
    cnt = 0
    """""
    while not stop_event.is_set():
            data = stream.read(chunk)
            frames.append(data)
    
    while recording:
        data = stream.read(chunk)
        frames.append(data)
    """
    while cnt < 10000:
        data = stream.read(chunk)
        frames.append(data)
        cnt += 1

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
    
    print("Gravação concluída.")
    await websocket.send("Gravação concluída. Ficheiro salvo como 'output.wav'.")

async def client():
    global recording
    recording = False
    uri = "ws://localhost:8005"
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Conectado ao servidor WebSocket!")

           
            stop_event = asyncio.Event()
            while True:
                command = await websocket.recv()
                print(f"📩 Comando recebido: {command}")
                if command == "gravar":
                    
                    if not recording:
                        recording = True
                        await websocket.send("Gravando...")
                        asyncio.create_task(recordAudio(stop_event,websocket))
                    """
                    if not stop_event.is_set():
                        stop_event.clear()
                        asyncio.create_task(recordAudio(stop_event, websocket))
                    """""
                elif command == "terminar":
                    if recording:
                       recording = False
                     #  await websocket.send("Gravação concluída. Ficheiro salvo como 'output.wav'.")
                    #if not stop_event.is_set():
                     #   stop_event.set()
                        #await websocket.send("Gravação concluída. Ficheiro salvo como 'output.wav'.")
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")

asyncio.run(client())




if __name__ == "__main__":
    #asyncio.run(connect())
    asyncio.run(client())
