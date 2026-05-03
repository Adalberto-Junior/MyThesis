#================================================================================================
#================================================================================================
# Project: Assistant to speech Therapy
# File: exerciseModule.py
# Created by: Adalberto Jr
# Created date: 24/03/2025
# Version: 1.0
# Python: 3.10
# Local: Universidade de Aveiro
# Description: This module is responsible for creating and managing exercises.
# ================================================================================================
#=================================================================================================


# ===============================================================
# Imports
# ===============================================================
import asyncio
import os
import aioconsole
import copy
import json
import logging
import websockets
from datetime import datetime
from pathlib import Path
import sys

# ===============================================================
# Configuração do ambiente e paths
# ===============================================================
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root) + '\\WebAppAssistantV2\\Aplicaction')

from modules.Message import Message
from modules.collectionName import *
from modules.CreatDocumentToDB import *
from modules.moduloName import *

# ===============================================================
# Configuração do LOGGING
# ===============================================================
# Ensure the log folder exists
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler("logs/exercise_module.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===============================================================
# Configurações iniciais e variáveis globais
# ===============================================================
HOST = "localhost"
BROKER_URL = f"ws://{HOST}:8765"  # Endereço do broker local
AUTH_NAME = exercicioM  # Nome do módulo para autenticação
AUTH_TOKEN = "token_exercises_123"  # Token de autenticação (mudar para algo mais seguro)

# Sessões e estado
session = {}
currentExercise = {}
exerciseList = []
exerciseBanc = []
currentStep = 77
exerciseType = None

# Reabilitação
exerciseRehabilitationList = []
currentExerciseRehabilitation = {}

# Mapeamento de tipos de exercício
exercise_mapping = {
    "articulação": "articulation",
    "fonologia": "phonology",
    "glotal": "glotta",
    "reapreendizagem": "Reapreendizagem",
    "fonacao": "phonation",
    "leitura": "Atividades de Leitura",
    "repetição de palavras": "Repetição de Palavras",
    "repetição de frases": "Repetição de Frases",
    "discurso espontâneo": "Discurso Espontâneo",
    "repetição de sílabas": "Diadococinésia",
}


# ===============================================================
# Autenticação com o broker
# ===============================================================
async def authenticate_with_broker(broker, timeout=10):
    """
    Realiza o processo de autenticação com o broker.
    Envia um token ou identificação do módulo antes de iniciar o processamento.
    """
    try:
        logger.info("Autenticando com o broker...")
        auth_payload = json.dumps({
           "auth": {
                "name": AUTH_NAME,
                "token": AUTH_TOKEN
            }
        })
        await broker.send(auth_payload)
        logger.info("Credenciais de autenticação enviadas ao broker.")

        response = await asyncio.wait_for(broker.recv(), timeout=timeout)

        logger.info(f"Resposta do broker após autenticação: {response}")

        if response:
            try:
                resp_json = safe_load_json(response)
                
                if 'status' in resp_json and (resp_json['status'].lower() == 'ok' or resp_json.get("status").lower() == "authenticated"):
                    logger.info("Autenticação com o broker bem-sucedida ✅")
                    return True
                else:
                    logger.warning(f"Falha na autenticação com o broker: {resp_json}")
                    return False
            except json.JSONDecodeError:
                logger.warning("Resposta do broker não é um JSON válido.")
                if isinstance(response, str) and (response.lower().find("ok") != -1 or response.lower().find("authenticated") != -1):
                    logger.info("Autenticação com o broker bem-sucedida ✅")
                    return True
                logger.warning(f"Falha na autenticação com o broker: {response}")
                return False
            except Exception as e:
                logger.exception(f"Erro ao processar a resposta do broker: {e}")

        logger.warning("Nenhuma resposta recebida do broker após autenticação.")
        return False
    
    except (asyncio.TimeoutError, websockets.ConnectionClosed):
        logger.exception("Timeout/Conexão fechada durante autenticação")
        return False
    except Exception:
        logger.exception("Erro inesperado durante autenticação")
        return False


# ===============================================================
# Função principal de tratamento de mensagens
# ===============================================================
async def handle(broker):
    """
    Lida com todas as mensagens recebidas do broker relacionadas ao módulo de exercício.
    Mantém compatibilidade com a lógica original; logs, validações e tratamento de erros incluídos.
    """
    global session, currentExercise, exerciseList, exerciseType
    global exerciseBanc, currentStep, exerciseRehabilitationList, currentExerciseRehabilitation

    # Tenta autenticar com o broker antes de processar
    authed = await authenticate_with_broker(broker)
    if not authed:
        logger.error("Não autenticado pelo broker. Saindo da função handle.")
        return

    async for message in broker:
        try:
            # Mensagem simple "Seu ID é ..." do broker (handshake inicial)
            if isinstance(message, str) and "Seu ID é" in message:
                my_id = message.split()[-1]
                logger.info("Broker assigned ID: %s", my_id)
                await broker.send(f"My name is: {exercicioM}")
                continue

            # Tenta parse JSON
            try:  
                messag = safe_load_json(message)
            except json.JSONDecodeError:
                logger.error("Erro ao decodificar JSON: %s", message)
                continue
            except Exception as e:
                logger.exception("Erro inesperado ao processar mensagem: %s", e)
                continue

            logger.info("Mensagem recebida: %s", messag)

            cmd = messag.get("command", "")

            # ----------------------------
            # 1) Pedido: enviar exercícios (sendMeExercise)
            # ----------------------------
            if cmd == "sendMeExercise":
                if not session:
                    logger.warning("sendMeExercise pedido mas sem sessão ativa.")
                    sms = Message(source=exercicioM, message="No user connected", command="noUserConnected", destination=assistente)
                    await broker.send(sms.get_message())
                    continue

                # Se messag['message'] contiver um JSON com "state", interpretamos
                isValideJson = await is_valid_json(messag.get("message", ""))
                query = {"userName": session['name'], "user": session['userId']}
                out_command = "getExerciseList"

                if isValideJson:
                    req = safe_load_json(messag.get("message", ""))
                    state = req.get("state", "").lower() if "state" in req else ""
                    if state == "continue_from_middle":
                        if 'exercise' in req:
                            query = {'exercise': req['exercise']}
                            out_command = "getExercise"
                            currentStep = req.get('currentStep', 77)
                    elif state == "continue_from_start":
                        exerciseBanc = req.get('exercise', [])

                sms = Message(source=exercicioM, message=json.dumps(query), command=out_command, destination=gestorDados)
                await broker.send(sms.get_message())
                logger.info("Pedido enviado ao gestorDados para obter exercícios (command=%s).", out_command)
                continue

            # ----------------------------
            # 2) Pedido: exercício por tipo (sendMeThisExerciseType)
            # ----------------------------
            if cmd == "sendMeThisExerciseType":
                if not session:
                    logger.warning("sendMeThisExerciseType pedido sem sessão.")
                    sms = Message(source=exercicioM, message="No user connected", command="noUserConnected", destination=assistente)
                    await broker.send(sms.get_message())
                    continue

                type_original = messag.get('message', "").lower().strip()
                exerciseType = type_original  # guarda string original

                # tenta encontrar correspondência no dicionário (partial match)
                type_found = None
                for keyword, mapped in exercise_mapping.items():
                    if keyword in type_original:
                        type_found = mapped
                        break

                # Monta query consoante tipo encontrado
                query = {"userName": session['name'], "user": session['userId']}
                if type_found:
                    # alguns tipos são processamentos
                    if type_found.lower() in ("articulation", "phonology", "glotta", "reapreendizagem", "phonation"):
                        query["typeOfProcessing"] = type_found
                    else:
                        query["type"] = type_found

                sms = Message(source=exercicioM, message=json.dumps(query), command="getExercise", destination=gestorDados)
                await broker.send(sms.get_message())
                logger.info("Pedido de exercícios por tipo enviado: %s", query)
                continue

            # ----------------------------
            # 3) Resposta do gestor de dados: envio de exercício(s) (retorningExercise)
            # ----------------------------
            if cmd == "retorningExercise":
                payload = messag.get('message', '')
                logger.info("retorningExercise payload recebido.")
                
                exerciseList = safe_load_json(payload) if payload else None

                # Se for lista
                if isinstance(exerciseList, list):
                    if len(exerciseList) > 0:
                        # aplica filtro por exerciseBanc se existir (manter ordem do exerciseBanc)
                        if exerciseBanc:
                            filtered = []
                            for eid in exerciseBanc:
                                for ex in exerciseList:
                                    if ex.get('_id') == eid:
                                        filtered.append(ex)
                                        break
                            exerciseList = filtered

                        # pega primeiro exercício e atualiza currentExercise
                        first = exerciseList[0]
                        exerciseList = exerciseList[1:]
                        currentExercise = first
                        logger.info("Exercício atual definido: %s", first.get('_id'))
                    else:
                        currentExercise = {}
                        logger.info("Nenhum exercício encontrado (lista vazia).")
                        sms = Message(source=exercicioM, message="Nenhum exercício encontrado.", command="noExerciseFound", destination=assistente)
                        await broker.send(sms.get_message())

                # Se for um único documento (dicionário)
                elif isinstance(exerciseList, dict):
                    # Se houve um currentStep guardado (continuação), corta steps
                    if currentStep != 77 and "steps" in exerciseList and isinstance(exerciseList['steps'], list):
                        exerciseList['steps'] = exerciseList['steps'][currentStep:]
                        logger.info("Ajustado steps por currentStep=%s", currentStep)

                    currentExercise = exerciseList
                    exerciseList = []
                    logger.info("Exercício (único) carregado: %s", currentExercise.get('_id'))

                else:
                    currentExercise = {}
                    logger.info("Resposta retorningExercise inválida.")
                    sms = Message(source=exercicioM, message="Nenhum exercício encontrado.", command="noExerciseFound", destination=assistente)
                    await broker.send(sms.get_message())

                # envia currentExercise para o assistente (broadcast)
                if currentExercise:
                    sms = Message(source=exercicioM, message=json.dumps(currentExercise), command="sendingExercise", destination=None)
                    await broker.send(sms.get_message())
                continue

            # ----------------------------
            # 4) Não existe tipo solicitado (thereIsNoType)
            # ----------------------------
            if cmd == "thereIsNoType":
                logger.info("Tipo solicitado não existe na base de dados: %s", exerciseType)
                sms = Message(
                    source=exercicioM,
                    message=f"Não existe nenhum exercício do tipo {exerciseType} na base de dados.",
                    command="ExerciseError",
                    destination=assistente
                )
                await broker.send(sms.get_message())
                continue

            # ----------------------------
            # 5) Pedido: próximo exercício na fila (sendMeNextExerciseInQueue)
            # ----------------------------
            if cmd == "sendMeNextExerciseInQueue":
                logger.info("Pedido para enviar próximo exercício na fila.")
                if isinstance(exerciseList, list):
                    if len(exerciseList) > 0:
                        first = exerciseList[0]
                        exerciseList = exerciseList[1:]
                        currentExercise = first
                        logger.info("Próximo exercício definido (lista): %s", first.get('_id'))
                    else:
                        currentExercise = {}
                        sms = Message(source=exercicioM, message="Já terminamos todos os exercícios.", command="theExercisesAreFinished", destination=assistente)
                        await broker.send(sms.get_message())
                else:
                    # exerciseList pode ser dict (único exercício)
                    if exerciseList:
                        currentExercise = exerciseList
                        exerciseList = []
                    else:
                        currentExercise = {}
                        sms = Message(source=exercicioM, message="Já terminamos todos os exercícios.", command="theExercisesAreFinished", destination=assistente)
                        await broker.send(sms.get_message())

                if currentExercise:
                    sms = Message(source=exercicioM, message=json.dumps(currentExercise), command="sendingExercise", destination=None)
                    await broker.send(sms.get_message())
                continue

            # ----------------------------
            # 6) Pausar diagnóstico (pausar_o_diagnostico)
            # ----------------------------
            if cmd == "pausar_o_diagnostico":
                logger.info("Processando pedido de pausar o diagnóstico.")
                # Se exerciseList é lista -> guardamos IDs
                if isinstance(exerciseList, list):
                    if len(exerciseList) > 0:
                        doc = {'exercise': [], 'user': session['userId'], 'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'state': 'start'}
                        for ex in exerciseList:
                            doc['exercise'].append(ex.get('_id'))
                        sms = Message(source=exercicioM, message=json.dumps(doc), command="pauseDiagnostic", destination=gestorDados)
                        await broker.send(sms.get_message())
                        exerciseList.clear()
                        logger.info("Estado do diagnóstico guardado (lista).")
                    else:
                        sms = Message(source=exercicioM, message="Já terminamos todos os exercícios. Não há necessidade de pausar a análise.", command="theExercisesAreFinished", destination=assistente)
                        await broker.send(sms.get_message())
                else:
                    # exerciseList pode ser dict (único exercício)
                    if exerciseList:
                        doc = {'exercise': [exerciseList.get('_id')], 'user': session['userId'], 'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'state': 'start'}
                        sms = Message(source=exercicioM, message=json.dumps(doc), command="pauseDiagnostic", destination=gestorDados)
                        await broker.send(sms.get_message())
                        exerciseList.clear()
                        logger.info("Estado do diagnóstico guardado (único exercício).")
                    else:
                        sms = Message(source=exercicioM, message="Já terminamos todos os exercícios. Não há necessidade de pausar a análise.", command="theExercisesAreFinished", destination=assistente)
                        await broker.send(sms.get_message())
                continue

            # ----------------------------
            # 7) Exercícios de reabilitação retornados (returningRehabilitationExercise)
            # ----------------------------
            if cmd == "returningRehabilitationExercise":
                payload = messag.get('message', '')
                
                exerciseRehabilitationList = safe_load_json(payload) if payload else None

                if isinstance(exerciseRehabilitationList, list):
                    if len(exerciseRehabilitationList) > 0:
                        first = exerciseRehabilitationList[0]
                        exerciseRehabilitationList = exerciseRehabilitationList[1:]
                        currentExerciseRehabilitation = first
                        logger.info("Exercício de reabilitação carregado: %s", first.get('_id'))
                    else:
                        currentExerciseRehabilitation = {}
                        sms = Message(source=exercicioM, message="Nenhum exercício encontrado.", command="noExerciseFound", destination=assistente)
                        await broker.send(sms.get_message())
                elif isinstance(exerciseRehabilitationList, dict):
                    currentExerciseRehabilitation = exerciseRehabilitationList
                else:
                    currentExerciseRehabilitation = {}
                    sms = Message(source=exercicioM, message="Nenhum exercício encontrado.", command="noExerciseFound", destination=assistente)
                    await broker.send(sms.get_message())

                if currentExerciseRehabilitation:
                    sms = Message(source=exercicioM, message=json.dumps(currentExerciseRehabilitation), command="sendingRehabilitationExercise", destination=None)
                    await broker.send(sms.get_message())
                continue

            # ----------------------------
            # 8) Começar reabilitação (comecar_reabilitacao)
            # ----------------------------
            if cmd == "comecar_reabilitacao":
                if not session:
                    logger.warning("Pedido de começar reabilitação sem sessão.")
                    sms = Message(source=exercicioM, message="No user connected", command="noUserConnected", destination=assistente)
                    await broker.send(sms.get_message())
                    continue

                query = {"userName": session['name'], "user": session['userId']}
                sms = Message(source=exercicioM, message=json.dumps(query), command="startRehabilitation", destination=gestorDados)
                await broker.send(sms.get_message())
                logger.info("Pedido de startRehabilitation enviado ao gestorDados.")
                continue

            # ----------------------------
            # 9) Atualização de sessão / logout
            # ----------------------------
            if cmd == 'currentSession':
                try:
                    
                    session = safe_load_json(messag.get('message', '{}'))
                    if not session:
                        logger.warning("currentSession recebido inválido: %s", messag.get('message', ''))
                        continue

                    logger.info("Sessão atualizada: %s", session.get('name'))
                except Exception as e:
                    logger.exception("Erro a fazer parse do currentSession: %s", e)
                continue

            if cmd == 'logout':
                session.clear()
                currentExercise = {}
                exerciseList = []
                exerciseBanc = []
                logger.info("Sessão encerrada (logout).")
                continue

            if cmd == 'confirmation':
                logger.info("Confirmação de recebimento recebida do {source}: %s", messag.get("source", "unknown"))
                continue

            # ----------------------------
            # Comando desconhecido
            # ----------------------------
            logger.warning("Comando não tratado recebido: %s", cmd)

        except json.JSONDecodeError as e:
            logger.error("Erro ao decodificar JSON: %s", e)
        except Exception as e:
            logger.exception("Erro ao processar mensagem no handle: %s", e)



# ===============================================================
# Funções auxiliares
# ===============================================================
async def is_valid_json(json_string):
    """Verifica se uma string é um JSON válido."""
    try:
        json.loads(json_string)
        return True
    except json.JSONDecodeError:
        return False

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


async def monitor_keyboard():
    """Monitora o teclado e permite reiniciar o módulo com ENTER."""
    while True:
        await aioconsole.ainput("Pressione ENTER para reiniciar...\n")
        logger.info("Reiniciando módulo...")
        os.execl(sys.executable, sys.executable, *sys.argv)


# ===============================================================
# Main: loop principal de reconexão e execução
# ===============================================================
async def main():
    """Função principal que mantém o módulo conectado ao broker."""
    while True:
        try:
            logger.info("Tentando conectar ao broker...")
            async with websockets.connect(BROKER_URL) as local_websocket:
                logger.info("Conectado ao broker com sucesso!")

                # Cria tarefas assíncronas
                task1 = asyncio.create_task(handle(local_websocket))
                task2 = asyncio.create_task(monitor_keyboard())

                await asyncio.gather(task1, task2)

        except (websockets.ConnectionClosed, ConnectionRefusedError) as e:
            logger.warning(f"Erro de conexão: {e}. Tentando reconectar em 5 segundos...")
            await asyncio.sleep(5)

        except Exception as e:
            logger.exception(f"Erro inesperado: {e}. Reiniciando em 5 segundos...")
            await asyncio.sleep(5)


# ===============================================================
# Execução direta
# ===============================================================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Encerrando módulo de exercício manualmente...")

