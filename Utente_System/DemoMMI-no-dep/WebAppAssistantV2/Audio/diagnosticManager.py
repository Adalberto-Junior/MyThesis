
import asyncio
import websocket
import sys
import json
import requests
import threading
import pyaudio
import wave
import time
import ssl
import pygame

#host = "localhost"
#uri = f"wss://{host}:8005/IM/USER1/APP"

# Endereço do servidor WebSocket
host = "localhost"
mmiCli_Out_add = f"wss://{host}:8005/IM/USER1/APP"

mmiCli_1 = "https://"+host+":8000/IM/USER1/APPSPEECH"

# Função de manipulação de mensagens recebidas
def im1_message_handler(ws, message):
    print(f"Mensagem recebida: {message}")
    filename = "exercicio.txt"
    currentExerciseId = 0

    if message != None and message != "RENEW" and message != "OK":
        print("Mensagem recebida: ", message)
        content = message.find("emma\\:interpretation").first().text().trim()
        if type(content) == str:
            try:
                data = json.loads(content)
                if data['nlu']['intent'] == "communication_skills":
                    exercise = ""
                    with open(filename,'r') as file:
                        exercise = file.read()
                    for line in exercise:
                        lineSplit = line.split("|")
                        texto = ""
                        if lineSplit[0] != "Introdução":
                            exerciseId= lineSplit[0].split("_")
                            texto = exerciseId[0] + " " + exerciseId[1] + " " + lineSplit[1]
                            currentExerciseId = int(exerciseId[1])
                        else:
                            texto = lineSplit[1] + " " + "Vamos começar o exercício dentro de 10 segundos"

                        sendToVoice(texto)
                        if lineSplit[0] == "Introdução":
                            time.sleep(10)
                        else:
                            lineSplit[0] = lineSplit[0] + ".wav"
                            recordAudio(30,lineSplit[0])
                            time.sleep(5)
                elif data['nlu']['intent'] == "request_Diagnostic_data":
                    # Buscar os dados do diagnóstico na base de dados
                    sendToVoice("Aqui estão os dados do diagnóstico")
                elif data['nlu']['intent'] == "continue_later":
                    # Salvar o progresso do exercício
                    with open('progress.txt','w') as file:
                        file.write(str(currentExerciseId) + "\n")
                        
                    sendToVoice("Seu progresso foi salvo")
                          
            except Exception as e:
                print("Erro ao processar mensagem: ", e)
        else:
            print("Erro ao processar mensagem: ", content)
    else:
        print("Mensagem inválida: ", message)


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

def configAudio():
    # Configuração do dispositivo de áudio
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    fs = 44100

    p = pyaudio.PyAudio()
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    input=True,
                    frames_per_buffer=chunk)
    return stream, p

def finishAudio(stream,p):
    stream.stop_stream()
    stream.close()
    p.terminate()

def saveAudio(frames,p,audioTitle):
    # Salva o arquivo de áudio
    if audioTitle == None:
        audioTitle = "output.wav"

    wf = wave.open(audioTitle, "wb")
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(44100)
    wf.writeframes(b''.join(frames))
    wf.close()

def recordAudio(seconds,filename):
    frames = []
    cnt = 0
    """""
    while not stop_event.is_set():
            data = stream.read(chunk)
            frames.append(data)
    """
    """""
    while True:
        data = stream.read(chunk)
        frames.append(data)
    """
    
    stream, p = configAudio()
    print("Gravando...")
    frames = []
    for i in range(0, int(44100 / 1024 * seconds)):
        data = stream.read(1024)
        frames.append(data)
    print("Gravação finalizada.")
    finishAudio(stream,p)
    print("Salvando arquivo de áudio...")
    saveAudio(frames,p,filename)


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

def sendToVoice(texto):
    speak = f"""
    <speak version=\"1.0\" xmlns=\"http://www.w3.org/2001/10/synthesis\"
    xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" 
    xsi:schemaLocation=\"http://www.w3.org/2001/10/synthesis http://www.w3.org/TR/speech-synthesis/synthesis.xsd\" 
    xml:lang=\"pt-PT\"><p>
    "{texto}"</p>
    </speak>
    """

    #EMMA
    emma_data = {
        "emma:id": "text-",
        "emma:medium": "text",
        "emma:mode": "command",
        "emma:confidence": "1",
        "emma:start": "0",
        "command": json.dumps(speak)
    }

    #Lifecycle
    lifecycle_event = {
        "source":"APPSPEECH",
        "target":"IM",
        "requestId":"text-1",
        "context":"ctx-1",
        "data": emma_data
    }

    response = requests.post(mmiCli_1, json=lifecycle_event)

    if response.status_code == 200:
        print("Mensagem enviada com sucesso!")
    else:
        print("Erro ao enviar mensagem: ", response.status_code, response.text)


    


if __name__ == "__main__":
    #host = "localhost"
    #uri = f"wss://{host}:8005/IM/USER1/APP"
    #asyncio.run(mmi_client_socket(uri))
    open_socket()
    #main()

"""""
import asyncio
import websockets

async def websocket_client():
    host = "localhost"
    mmiCli_Out_add = f"wss://{host}:8005/IM/USER1/APP"
    uri = "ws://localhost:8005/IM/USER1/APP"  # Substitua pelo endereço correto do seu servidor mmi.js
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_cert_chain(certfile='cert.pem',keyfile='key.pem')

    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with websockets.connect(mmiCli_Out_add, ssl = ssl_context) as websocket:
        # Envia uma mensagem para o servidor
        mensagem = "Olá, mmi.js!"
        await websocket.send(mensagem)
        print(f"Mensagem enviada: {mensagem}")

        # Aguarda resposta
        resposta = await websocket.recv()
        print(f"Resposta recebida: {resposta}")

# Executa o cliente WebSocket
#asyncio.run(websocket_client())

if __name__ == "__main__":
    #host = "localhost"
    #uri = f"wss://{host}:8005/IM/USER1/APP"
    #asyncio.run(mmi_client_socket(uri))
    asyncio.run(websocket_client())

    #main()
"""""
"""""
import requests

host = "localhost"

url = f"https://"+host+":8000/IM/USER1/APPSPEECH" # Substitua pela URL correta do seu servidor mmi.js
payload = {
    "mmi:mmi": {
        "@xmlns:mmi": "http://www.w3.org/2008/04/mmi-arch",
        "mmi:version": "1.0",
        "mmi:ExtensionNotification": {
            "@mmi:context": "ctx-1",
            "@mmi:requestId": "text-1",
            "@mmi:source": "PYTHON_CLIENT",
            "@mmi:target": "IM",
            "mmi:data": {
                "emma:emma": {
                    "@xmlns:emma": "http://www.w3.org/2003/04/emma",
                    "emma:version": "1.0",
                    "emma:interpretation": {
                        "@emma:confidence": "1",
                        "@emma:id": "text-123",
                        "@emma:medium": "text",
                        "@emma:mode": "command",
                        "@emma:start": "0",
                        "command": {
                            "recognized": ["SPEECH", "APP"],
                            "text": "Mundo!",
                            "nlu": {
                                "intent": "change_color",
                                "shape": "quadrado",
                                "color": "azul"
                            }
                        }
                    }
                }
            }
        }
    }
}

headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload)

print("Status Code:", response.status_code)
print("Resposta:", response.text)
"""

