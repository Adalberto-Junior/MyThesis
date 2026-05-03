#Autor    : Adalberto Jr
#Data     : 17/02/2025
#Local    : UA, Aveiro
#Versão   : 1.0
#Descrição : Modulo responsavel por fazer diagnostico do user,  analisando os dados coletados e criar um ficheiro texto com os resultados

# diagnostico_client.py
import asyncio
import aioconsole
import websockets
import sys
import os
import json
import unicodedata
import re
import logging
from datetime import datetime
import pygame
from collections import deque
from pathlib import Path

# Ajuste de path para imports locais (manter)
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root) + r'\WebAppAssistantV2\Aplicaction')

# Módulos do teu projeto (mantidos)
from modules.Message import *
from modules.moduloName import *
from modules.Recorder import *
from modules.DataProcessor import *
from modules.CreatDocumentToDB import *

# ---------------------------
# Configurações / Constantes
# ---------------------------
MODULE_NAME = diagnosticoM               # nome do módulo para autenticação
MODULE_TOKEN = "token_diag_123"           # token do módulo (deve coincidir com o broker)
host = "localhost"
urlLocal = f"ws://{host}:8765"                   # endereço do broker local

# Ensure the log folder exists
os.makedirs("logs", exist_ok=True)

LOG_FILE = "logs/diagnostico.log"

# Mensagens mapeadas
messageToRetorn = {
    "ready": "readyToRecord",
    "next": "nextExercise",
    "stopped": "recordingStopped",
    "pause": "pauseDiagnostic",
    "done": "processedData",
    "getExercise": "sendMeExercise",
    "getExerciseTypeX": "sendMeThisExerciseType",
    "getNextExercise": "sendMeNextExerciseInQueue",
    "getReport": "getMeThisReport",
    "continueTheDiagnostic": "getMeTheLastState",
    "sendingCurrentStep": "currentStep",
    "readyToStart": "weCanStart"
}

# ---------------------------
# Estado global (conservado da lógica original)
# ---------------------------
filename = "../../ficheiro/exercicio.txt"
exerciseDic = {}
currentExerciseId = 0
queue = deque()

session = {}
currentExercise = {}
currentStep = 0

audioNameIndex = 0
audioToProcessing = {
    "audioToArticulation": [],
    "audioToPhonation": [],
    "audioToGlottal": [],
    "audioToReplearning": [],
    "audioToProsody": [],
    "audioToPhonological": [],
}
currentKeyOfAudioProcessing = []

# ---------------------------
# Logging
# ---------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("diagnostico")

# ---------------------------
# Helpers utilitários
# ---------------------------

async def sanitizar_nome(nome: str) -> str:
    """Sanitiza nomes para usar em paths (remove acentos, caracteres inválidos)."""
    nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('utf-8')
    nome = nome.replace(' ', '_')
    nome = re.sub(r'[<>:"/\\|?*]', '', nome)
    return nome

async def criar_pasta_utilizador(base_path, nome_utilizador, audioName=None):
    caminho = os.path.join(base_path, nome_utilizador)
    os.makedirs(caminho, exist_ok=True)
    return os.path.abspath(caminho)

async def zipar_ficheiros(caminho_zip, ficheiros):
    import zipfile
    try:
        with zipfile.ZipFile(caminho_zip, 'w') as zipf:
            for ficheiro in ficheiros:
                zipf.write(ficheiro, os.path.basename(ficheiro))
        logger.info("Zip criado: %s", caminho_zip)
    except Exception:
        logger.exception("Erro ao zipar ficheiros")

async def returnListOfResult(data, static=False):
    listOfResult = []
    for key, value in data.items():
        result = {key: value}
        listOfResult.append(result)
    return listOfResult

async def clearData():
    global audioNameIndex, audioToProcessing, currentKeyOfAudioProcessing
    audioNameIndex = 0
    for key in audioToProcessing.keys():
        audioToProcessing[key].clear()
    currentKeyOfAudioProcessing.clear()
    logger.debug("Dados de áudio limpos")

# ---------------------------
# Funções de gravação (wrapper)
# ---------------------------
async def start_recording(path, filename, seconds=None, vad=None):
    logger.info("Iniciando gravação: %s/%s (seconds=%s, vad=%s)", path, filename, seconds, vad)
    try:
        audio = Recorder(path=path, filename=filename, seconds=seconds if seconds else 10)
        if seconds:
            audio.record()
        elif vad:
            audio.record_vad()
        else:
            audio.start_recording_Key()
            audio.recording_thread.join()
        logger.info("Gravação concluída: %s", filename)
    except Exception:
        logger.exception("Erro ao gravar o audio")

# ---------------------------
# Função de autenticação (cliente)
# ---------------------------
async def authenticate_with_broker(broker_ws, timeout=10):
    """
    Envia credenciais ao broker e espera uma resposta JSON com 'status' == 'ok'
    Retorna True se autenticado, False caso contrário.
    """
    # auth_payload = json.dumps({"name": MODULE_NAME, "token": MODULE_TOKEN})
    auth_payload = json.dumps({"auth": {"name": MODULE_NAME, "token": MODULE_TOKEN}})
    try:
        await broker_ws.send(auth_payload)
        logger.info("Credenciais enviadas ao broker para autenticação")
        resp = await asyncio.wait_for(broker_ws.recv(), timeout=timeout)
        # Broker pode enviar string simples ou JSON; tentar analisar
        try:
            resp_json = safe_load_json(resp)
            status = resp_json.get("status") or resp_json.get("result") or None
            if status == "ok" or resp_json.get("status") == "ok" or resp_json.get("result") == "ok" or status == "authenticated" or resp_json.get("status") == "authenticated":
                logger.info("Autenticação com broker: OK")
                return True
            else:
                logger.warning("Resposta do broker (autenticação) não OK: %s", resp_json)
                return False
        except json.JSONDecodeError:
            # Se o broker respondeu com string (ex: "OK" ou "Autenticado"), aceitar se contiver "ok"/"OK"
            if isinstance(resp, str) and (resp.lower().find("ok") != -1 or resp.lower().find("authenticated") != -1):
                logger.info("Autenticação com broker: OK (resposta plain text)")
                return True
            logger.warning("Resposta do broker não é JSON e não contém 'ok' nem 'authenticated': %s", resp)
            return False
    except (asyncio.TimeoutError, websockets.ConnectionClosed):
        logger.exception("Timeout/Conexão fechada durante autenticação")
        return False
    except Exception:
        logger.exception("Erro inesperado durante autenticação")
        return False

# ---------------------------
# Função principal de handling das mensagens do broker
# ---------------------------
async def handle(broker):
    """
    Lê mensagens do broker (já autenticado) e processa comandos.
    A autenticação é feita antes de começar a processar a queue de mensagens.
    """
    global session, currentExercise, currentStep, currentExerciseId
    global audioNameIndex, audioToProcessing, currentKeyOfAudioProcessing

    logger.info("Handler iniciado")
    authenticated = await authenticate_with_broker(broker)
    if not authenticated:
        logger.error("Autenticação falhou. Encerrando handler.")
        return

    # sinalizar ao broker que estamos prontos, se necessário
    try:
        sms = Message(message="I'm reading", source=diagnosticoM, command=messageToRetorn['readyToStart'], destination=assistente)
        await broker.send(sms.get_message())
    except Exception:
        logger.exception("Erro ao enviar mensagem inicial ao broker")

    async for raw_message in broker:
        logger.debug("Mensagem bruta recebida do broker: %s", raw_message)
        try:
            if isinstance(raw_message, str) and "Seu ID é" in raw_message:
                # essa condição pode ocorrer dependendo do broker; apenas logar
                logger.info("Broker informou ID: %s", raw_message)
                continue

            messag = safe_load_json(raw_message)
            if not messag:
                logger.warning("Mensagem vazia ou inválida recebida: %s", raw_message)
                continue
            cmd = messag.get("command", "")
            msg_content = messag.get("message", "")

            # -------------------------
            # Casos de comando (mantive a tua lógica original, adaptada)
            # -------------------------
            if cmd == 'fazer_o_diagnostico':
                await clearData()
                sms = Message(message="I need exercise!", source=diagnosticoM, command=messageToRetorn['getExercise'], destination=exercicioM)
                await broker.send(sms.get_message())

            elif cmd == 'continuar_o_progresso':
                await clearData()
                query = {'user': session.get('userId')}
                sms = Message(message=json.dumps(query), source=diagnosticoM, command=messageToRetorn['continueTheDiagnostic'], destination=gestorDados)
                await broker.send(sms.get_message())

            elif cmd == 'fazer_exercicio_de_tipo':
                await clearData()
                sms = Message(message=messag.get("message", ""), source=diagnosticoM, command=messageToRetorn['getExerciseTypeX'], destination=exercicioM)
                await broker.send(sms.get_message())

            elif cmd == 'continuar_a_analise':
                await clearData()
                sms = Message(message="I need next exercise in queue!", source=diagnosticoM, command=messageToRetorn['getNextExercise'], destination=exercicioM)
                await broker.send(sms.get_message())

            elif cmd == 'pausar_o_diagnostico':
                try:
                    msg_obj = safe_load_json(messag.get("message", ""))
                except Exception:
                    msg_obj = {"raw": messag.get("message")}
                msg_obj['audio'] = json.dumps(audioToProcessing)
                msg_obj['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                sms = Message(message=json.dumps(msg_obj), source=diagnosticoM, command=messageToRetorn['pause'], destination=gestorDados)
                await broker.send(sms.get_message())

            elif cmd == "diagnosticPaused":
                currentExercise.clear()
                currentStep = 0
                await clearData()

            elif cmd == 'mostrar_o_diagnostico':
                query = {"utente_id": session.get('userId'), "status": "finalizado"}
                sms = Message(message=json.dumps(query), source=diagnosticoM, command=messageToRetorn['getReport'], destination=gestorDados)
                await broker.send(sms.get_message())

            elif cmd == 'currentSession':
                try:
                    session = safe_load_json(messag.get("message", ""))
                    if not isinstance(session, dict):
                        session = {}
                        logger.warning("currentSession não é um dict válido: %s", messag.get("message", ""))
                        continue

                    session['name'] = await sanitizar_nome(session.get('name', "").strip().replace(" ", "_"))
                    logger.info("Sessão armazenada: %s", session.get('name'))
                except Exception:
                    logger.exception("Erro ao processar currentSession")

            elif cmd == 'logout':
                session.clear()
                currentExercise.clear()
                currentStep = 0
                await clearData()
                logger.info("Logout processado")

            elif cmd == 'toRecord':
                # iniciar gravação do passo atual
                await process_to_record(broker, messag)

            elif cmd == 'recordingId':
                # atualiza ids dos áudios processados
                for key in currentKeyOfAudioProcessing:
                    if audioToProcessing.get(key) and len(audioToProcessing[key]) > audioNameIndex:
                        audioToProcessing[key][audioNameIndex]['id'] = messag.get('new_values')
                audioNameIndex += 1
                sms = Message(message="I finish this record, you can start next exercise!", source=diagnosticoM, command=messageToRetorn["next"], destination=assistente)
                await broker.send(sms.get_message())

            elif cmd == 'sendingExercise':
                # recebe o exercício
                try:
                    currentExercise = safe_load_json(messag.get("message", ""))
                    if not isinstance(currentExercise, dict):
                        currentExercise = {}
                        logger.warning("sendingExercise não é um dict válido: %s", messag.get("message", ""))
                        continue
                except Exception:
                    currentExercise = messag.get('message')
                await asyncio.sleep(0.25)
                if currentExercise:
                    sms = Message(message="I am ready to record!", source=diagnosticoM, command=messageToRetorn["ready"], destination=assistente)
                    await broker.send(sms.get_message())
                else:
                    sms = Message(source=diagnosticoM, message="Nenhum exercício encontrado.", command="noExerciseFound", destination=assistente)
                    await broker.send(sms.get_message())

            elif cmd == 'sendingLastState':
                await handle_sending_last_state(broker, messag)

            elif cmd == 'processTheData':
                await process_all_audio_and_send_results(broker)

            else:
                # eco básico
                if cmd == "confirmation":
                    logger.info("✅ Mensagem de confirmação recebida.")
                else:
                    logger.warning(f"⚠️ Comando desconhecido recebido: {cmd}. Mensagem: {msg_content}")
                #await broker.send(Message(message='recebido', source=diagnosticoM, command='confirmation', destination='').get_message())

        except json.JSONDecodeError:
            logger.exception("Erro ao decodificar JSON: %s", raw_message)
        except websockets.ConnectionClosed:
            logger.warning("Conexão com broker fechada (durante leitura)")
            break
        except Exception:
            logger.exception("Erro ao processar mensagem do broker")

# ---------------------------
# Funções menores usadas pelo handler (extraídas para clareza)
# ---------------------------

async def process_to_record(broker, messag):
    """Lógica para tratar o comando 'toRecord' (iniciar gravação)."""
    global currentExercise, currentStep, audioNameIndex, audioToProcessing, currentKeyOfAudioProcessing

    if not currentExercise:
        sms = Message(message="We currently do not have exercises to make a diagnostic", source=diagnosticoM, command="cancelTheRecord", destination=diagnosticoM)
        await broker.send(sms.get_message())
        return

    try:
        pygame.mixer.init()

        # obtém o step atual
        step_obj = currentExercise['steps'][0]
        stepId = step_obj.get('ID', '').strip().replace(" ", "_")
        currentStep += 1
        currentExercise['steps'] = currentExercise['steps'][1:]

        # se a mensagem contiver informação de step atual, tenta adaptar
        try:
            if messag.get('message') and ":" in messag['message']:
                arg = messag['message'].split(":", 1)[1].strip()
                possible_step = int(arg)
                # ajustar stepId se aplicável (proteção de índices)
                if 0 <= possible_step < len(currentExercise.get('steps', [])):
                    stepId = currentExercise['steps'][possible_step].get("ID", "").strip().replace(" ", "_")
        except Exception:
            logger.debug("Não foi possível extrair step da mensagem; prosseguindo com default")

        logger.info("Gravando exercício: %s step: %s", currentExercise.get('name'), stepId)

        # construir nome de ficheiro
        exerType = currentExercise.get('type', '').split()
        exerName = currentExercise.get('name', '').split()
        typeAcronym = "".join([s[:2].upper() for s in exerType if len(s) > 2])
        nameAcronym = "".join([s[:2].upper() for s in exerName if len(s) > 2])
        exerciseId = f"{typeAcronym}_{nameAcronym}_{stepId}"
        exerciseId = await sanitizar_nome(exerciseId.strip())

        audioName = f"{exerciseId}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

        # sinal de contagem regressiva
        pygame.mixer.music.load('../Audio_util/3_Second_Timer_start.mp3')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        nome_utilizador = await sanitizar_nome(session.get('name', '').strip().replace(" ", "_") if session else "guest")
        path = await criar_pasta_utilizador(
            base_path=r"..\Audio",
            nome_utilizador=nome_utilizador
        )

        # start recording (sincrónico com Recorder)
        await start_recording(path=path, filename=audioName, vad=True)

    
        # preparar dados de audio para processamento
        path = os.path.join(path, audioName.split(".")[0])
        fullPath = os.path.join(path, audioName)
        audioData = {
            'name': audioName,
            'step': stepId,
            'id': '',
            'path': fullPath,
            'type': currentExercise.get('type'),
        }

        # sinal de fim de gravação
        pygame.mixer.music.load('../Audio_util/finalDeAudio.mp3')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        # distribuir audioData nos diferentes processamentos
        types_proc = currentExercise.get('typeOfProcessing', [])
        if not isinstance(types_proc, list):
            types_proc = [types_proc]
        for key, bucket in audioToProcessing.items():
            for t in types_proc:
                if t.lower() in key.lower():
                    bucket.append(audioData)
                    if key not in currentKeyOfAudioProcessing:
                        currentKeyOfAudioProcessing.append(key)

        # criar documento e avisar gestor de dados
        document = CreatDocumentToDB()
        userId = session.get('userId', 77)
        exercise_doc = document.recordingDocument(
            name=audioName, path=fullPath, exercise=currentExercise.get('_id'),
            user=userId, time=datetime.now().strftime('%d-%m-%Y'),
            exerciseStep=stepId, userName=session.get('name', '')
        )

        sms = Message(source=diagnosticoM, message=exercise_doc, command="setRecording", destination=gestorDados)
        await broker.send(sms.get_message())

    except Exception:
        logger.exception("Erro durante process_to_record")

async def handle_sending_last_state(broker, messag):
    """Trata 'sendingLastState' recebido do broker (continua diagnóstico)."""
    global audioToProcessing, currentStep

    try:
        state = safe_load_json(messag.get('message', '{}'))
    except Exception:
        state = {}

    if not state:
        return

    if state.get("state", "").lower() == "middle":
        # state['audio'] pode ser string; garantir que é dict
        audio_field = state.get('audio')
        if isinstance(audio_field, str):
            try:
                audioToProcessing = safe_load_json(audio_field)
            except Exception:
                audioToProcessing = {}
        else:
            audioToProcessing = audio_field

        currentStep = int(state.get('currentStep', 1)) - 1
        query = {'currentStep': currentStep}
        sms = Message(message=json.dumps(query), source=diagnosticoM, command=messageToRetorn["sendingCurrentStep"], destination=assistente)
        await broker.send(sms.get_message())

        query = {'exercise': state.get('exercise'), 'currentStep': currentStep, 'user': state.get('user'), 'state': 'continue_from_middle'}
        sms = Message(message=json.dumps(query), source=diagnosticoM, command=messageToRetorn["getExercise"], destination=exercicioM)
        await broker.send(sms.get_message())
    else:
        query = {'exercise': state.get('exercise'), 'user': state.get('user'), 'state': 'continue_from_start'}
        sms = Message(message=json.dumps(query), source=diagnosticoM, command=messageToRetorn["getExercise"], destination=exercicioM)
        await broker.send(sms.get_message())

async def process_all_audio_and_send_results(broker):
    """
    Processa todos os áudios por tipo e envia documentos de resultado ao gestor de dados.
    Mantive a tua lógica, mas modularizei e tratei exceções.
    """
    try:
        global currentExercise, currentStep
        currentExercise.clear()
        currentStep = 0
        date = datetime.now().strftime('%d-%m-%Y')
        hour = datetime.now().hour

        diagnostico = DataProcessor()
        document = CreatDocumentToDB()

        # lista de pares (bucket_key, processing_fn_name, processing_type)
        processing_map = [
            ("audioToArticulation", diagnostico.articulationFeatures, "articulation"),
            ("audioToGlottal", diagnostico.glottalFeatures, "glottal"),
            ("audioToPhonation", diagnostico.phonationFeatures, "phonation"),
            ("audioToProsody", diagnostico.prosodyFeatures, "prosody"),
            ("audioToReplearning", diagnostico.replearningFeatures, "replearning"),
            ("audioToPhonological", diagnostico.phonologicalFeatures, "phonological"),
        ]

        for bucket_key, proc_fn, processing_type in processing_map:
            bucket = audioToProcessing.get(bucket_key, [])
            for audio in bucket:
                try:
                    result, pathToChart = proc_fn(audio=audio['path'], userName=session.get('name','').strip().replace(" ", "_"), step=audio['step'])
                    static_result = await returnListOfResult(result[0])
                    no_static_result = await returnListOfResult(result[1])
                    doc = document.resultDocument(
                        static_result=static_result,
                        no_static_result=no_static_result,
                        date=date,
                        recording=audio.get('id'),
                        step=audio.get('step'),
                        user=session.get('userId'),
                        processing_type=processing_type,
                        pathToChart=pathToChart,
                        hour=hour
                    )
                    sms = Message(source=diagnosticoM, message=doc, command="setResults", destination=gestorDados)
                    await broker.send(sms.get_message())
                except Exception:
                    logger.exception("Erro ao processar audio em %s: %s", bucket_key, audio.get('path'))

        # sinalizar conclusão ao assistente
        sms = Message(message="I finish the analize!", source=diagnosticoM, command=messageToRetorn["done"], destination=assistente)
        await broker.send(sms.get_message())

    except Exception:
        logger.exception("Erro no processamento de todos os áudios")


# --------------------------
# Funções Auxiliares
# --------------------------
def safe_load_json(data):
    """
    Garante que o resultado seja SEMPRE um dict ou list válido.
    Aceita:
      - dict (retorna igual)
      - list (retorna igual)
      - JSON string normal
      - JSON duplo
      - strings inválidas (retorna None)
    """
    # 1. Se já é dict ou lista → OK
    if isinstance(data, (dict, list)):
        return data

    # 2. Se não é string → inválido
    if not isinstance(data, str):
        logger.warning(f"safe_load_json recebeu tipo inesperado: {type(data)} → {data}")
        return None

    # 3. Se é string, tentamos decodificar
    try:
        decoded = json.loads(data)

        # json.loads() devolveu outra string? → JSON duplo
        if isinstance(decoded, str):
            try:
                decoded2 = json.loads(decoded)
                return decoded2
            except Exception:
                # Não era duplo, devolve a string original
                return decoded

        # Se chegou aqui → é dict ou list válido
        return decoded

    except json.JSONDecodeError:
        logger.error(f"safe_load_json falhou ao decodificar: {data}")
        return None

# ---------------------------
# Monitor teclado (reiniciar)
# ---------------------------
async def monitor_keyboard():
    while True:
        await aioconsole.ainput("Pressione ENTER para reiniciar...\n")
        logger.info("Reiniciando módulo diagnostico via teclado")
        os.execl(sys.executable, sys.executable, *sys.argv)

# ---------------------------
# Loop principal / reconexão
# ---------------------------
async def main():
    logger.info("Iniciando modulo Diagnóstico (cliente)")

    while True:
        try:
            logger.info("Tentando conectar ao broker: %s", urlLocal)
            async with websockets.connect(urlLocal) as local_websocket_2:
                logger.info("Conectado ao broker com sucesso")
                # cria tarefas
                task1 = asyncio.create_task(handle(local_websocket_2))
                task2 = asyncio.create_task(monitor_keyboard())
                # aguarda qualquer término (ou exceção)
                done, pending = await asyncio.wait([task1, task2], return_when=asyncio.FIRST_EXCEPTION)
                for task in pending:
                    task.cancel()
                for task in done:
                    if task.exception():
                        raise task.exception()
        except (websockets.ConnectionClosed, ConnectionRefusedError) as e:
            logger.warning("Erro de conexão: %s. Tentando reconectar em 5s...", e)
            await asyncio.sleep(5)
        except Exception:
            logger.exception("Erro inesperado no main. Reiniciando em 5s...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Módulo Diagnóstico encerrado manualmente")
    except Exception:
        logger.exception("Erro fatal - encerrando")
