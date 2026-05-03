#==================================================================================================
#Autor    : Adalberto Jr
#Data     : 21/03/2025
#Local    : UA, Aveiro
#Versão   : 1.0
#Descrição : Modulo responsavel por gerenciar os dados do sistema e comunicar com a base de dados MongoDB para armazenar e recuperar dados
#===============================================================================================

import asyncio
import math
import os
import stat
import ctypes
import aioconsole
import websockets
import sys
import json
import logging
from bson import ObjectId
from pymongo import cursor
import requests
from collections import deque
from pathlib import Path

# ============================================
# CONFIGURAÇÃO DO LOGGING
# ============================================

# Ensure the log folder exists
os.makedirs("logs", exist_ok=True)

# Cria logger
logger = logging.getLogger("DataManager")
logger.setLevel(logging.DEBUG)

# Formato do log
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Handler para consola
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Handler para ficheiro
file_handler = logging.FileHandler("logs/data_manager.log", encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# ============================================
# IMPORTAÇÕES DE MÓDULOS INTERNOS
# ============================================

path_root = Path(__file__).parents[2]
sys.path.append(str(path_root) + r'\WebAppAssistantV2\Aplicaction')

from modules.Message import *
from modules.moduloName import *
from modules.Database import *
from modules.collectionName import *
from modules.APIClient import APIClient

# ============================================
# CONFIGURAÇÕES GERAIS
# ============================================

# Endereços fixos
HOST = "localhost"
urlLocal = f"ws://{HOST}:8765"  # Endereço do broker local
# api = APIClient("http://localhost:5000/casa_viva/home")

currentUser = {}

# 🔐 Token e nome do módulo
BROKER_NAME = gestorDados
BROKER_TOKEN = "token_data_123"

# ============================================
# MAPEAMENTO DE COMANDOS
# ============================================

messageToRetorn = {
    "getUser": "retorningUser",
    "getExercise": "retorningExercise",
    "getRecording": "retorningRecording",
    "getResults": "retorningResults",
    "getSession": "retorningSession",
    "getScheduling": "returningSchedule",
    "setData": "storedData",
    "delete": "deletedData",
    "update": "updatedData",
    "problem": "errorData",
    'sendRecordingId': 'recordingId',
    'notFoundType': 'thereIsNoType',
    'notFound': 'thereIsNoData',
    'login': 'loggedIn',
    'logout': 'logout',
    'registerUser': 'UserRegistered',
    'getReport': 'returningReport',
    'pauseDiagnostic': 'diagnosticPaused',
    'errorPausingDiagnostic': 'errorPausingDiag',
    'sendMeTheLastState': 'sendingLastState',
    'currentUser': 'currentSession',
    'setResults': 'resultWasSave',
    'rehabilitationResults': 'returningRehabilitationExercise'
}

# ============================================
# CLASSE PARA JSON ENCODER
# ============================================

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)


# import json
# import logging
# from bson import cursor
# from utils import (
#     convert_to_document, convert_to_ObjectId,
#     send_problematic_message, send_not_found_message,
#     send_invalid_command, Message, JSONEncoder,
#     enviar_audio_para_backend, enviar_imagem_para_backend, deleteFile,
#     detect_collection
# )
# from api_client import APIClient

# ===================== CONFIGURAÇÃO DO LOGGING =====================
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s [%(levelname)s] %(message)s',
#     handlers=[
#         logging.FileHandler("app.log"),  # Grava no diretório raiz
#         logging.StreamHandler()          # Mostra no terminal
#     ]
# )
# logger = logging.getLogger(__name__)

# ===================== FUNÇÃO PRINCIPAL =====================
async def handle1(broker):
    """
    Processa mensagens recebidas do broker, executando operações CRUD
    e comandos específicos (login, logout, startRehabilitation, etc.)
    conforme a estrutura do projeto.
    """
    global currentUser
    api = APIClient("http://localhost:5000/casa_viva/home")
    auth_api = APIClient("http://localhost:5000/casa_viva/home/auth")

    auth_payload = json.dumps({"auth": {"name": BROKER_NAME, "token": BROKER_TOKEN}})

    # 🔐 Envia credenciais de autenticação ao broker
    await broker.send(auth_payload)
    logger.info("Credenciais de autenticação enviadas ao broker.")

    # 🕵️‍♂️ Aguarda resposta do servidor
    auth_response = await broker.recv()
    logger.info(f"Resposta de autenticação do servidor: {auth_response}")

    if auth_response:
        try:
            auth_data = safe_load_json(auth_response)
            # auth_data = json.loads(auth_response)
        except json.JSONDecodeError:
            logger.error("Resposta de autenticação inválida.")
            return

        if not auth_data:
            logger.error(f"Resposta de autenticação vazia ou inválida.{auth_response}")
            await broker.close()
            return
        
        if auth_data.get("status") != "authenticated":
            logger.error("Falha na autenticação com o broker.")
            await broker.close()
            return
        logger.info("Autenticação com o broker bem-sucedida.")

    else:
        logger.error("Nenhuma resposta de autenticação recebida.")
        await broker.close()
        return
        

    async for message in broker:
        # if "seu id é" in message.lower():
        #     my_id = message.split()[-1].strip()
        #     logger.info(f"Identificado ID do servidor: {my_id}")
        #     await broker.send(f"My name is: {gestorDados}")
        #     continue
        

        try:
            msg = safe_load_json(message)
            # msg = json.loads(message)
            if not msg:
                logger.warning(f"Mensagem vazia ou inválida recebida.{message}")
                continue

            command = msg.get('command', '').lower()

            if "confirmation" in command:
                logger.info(f"✅ Mensagem de confirmação recebida do {msg.get('source', 'desconhecido')}.")
                continue  # Ignorar mensagens de confirmação
            
            document = await convert_to_document(msg.get("message")) if "logout" not in command else {}

            if not document and "logout" not in command:
                await send_problematic_message(broker, msg, "Formato de documento inválido.")
                continue

            # ================= LOGIN =================
            if "login" in command:
                await _handle_login(broker, msg, document, api)
                continue

            # ================= LOGOUT =================
            if "logout" in command:
                await _handle_logout(broker, msg, api)
                continue

            # ================= START REHABILITATION =================
            if "startrehabilitation" in command:
                await _handle_start_rehabilitation(broker, msg, document, api)
                continue

            # Detectar coleção
            collection = await detect_collection(command)
            if not collection:
                logger.warning(f"Coleção não detectada para o comando: {command}")
                await send_invalid_command(broker, msg)
                continue

            # ================= CRUD DISPATCH =================
            if "get" in command:
                await _handle_get(broker, msg, collection, document, api, auth_api, command)
            elif "set" in command:
                await _handle_set(broker, msg, collection, document, api, auth_api)
            elif "delete" in command:
                await _handle_delete(broker, msg, collection, document, api, auth_api)
            elif "update" in command:
                await _handle_update(broker, msg, collection, document, api, auth_api)
            elif "pausediagnostic" in command:
                await _handle_pause_diagnostic(broker, msg, collection, document, api)
            else:
                await send_invalid_command(broker, msg)

        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar mensagem JSON: {e}")
            continue
        except Exception as e:
            logger.exception(f"Erro inesperado ao processar mensagem: {e}")
            sms = Message(
                message="Erro ao processar mensagem.",
                source=gestorDados,
                command=messageToRetorn['problem'],
                destination=msg.get('source')
            )
            await broker.send(sms.get_message())
            continue


# ===================== HANDLERS AUXILIARES =====================

async def _handle_login(broker, msg, document, api):
    email = document.get('email')
    password = document.get('password')
    if not email or not password:
        await send_problematic_message(broker, msg, "Email e senha são obrigatórios para login.")
        return

    if api.login(email, password):
        sms = Message(
            message="Login bem-sucedido.",
            source=gestorDados,
            command=messageToRetorn['login'],
            destination=msg['source']
        )
        await broker.send(sms.get_message())

        user = api.get_user()
        if user:
            global currentUser
            currentUser = user
            sms = Message(
                message=json.dumps(user, cls=JSONEncoder),
                source=gestorDados,
                command=messageToRetorn['currentUser'],
                destination=None
            )
            await broker.send(sms.get_message())
    else:
        await send_problematic_message(broker, msg, "Erro ao fazer login. Verifique suas credenciais.")

async def _handle_logout(broker, msg, api):
    if api.logout():
        sms = Message(
            message="Logout feito com sucesso",
            source=gestorDados,
            command=messageToRetorn['logout'],
            destination=None
        )
        await broker.send(sms.get_message())
    else:
        await send_problematic_message(broker, msg, "Erro ao fazer logout.")

async def _handle_start_rehabilitation(broker, msg, document, api):
    user_id = document.get("user")
    if not user_id:
        await send_problematic_message(broker, msg, "ID do usuário é obrigatório para reabilitação.")
        return

    response = api.get("/rehabilitation/exercise")
    if response and response.status_code == 200:
        data = response.json()
        if isinstance(data, cursor.Cursor):
            data = list(data)
        sms = Message(
            message=json.dumps(data, cls=JSONEncoder),
            source=gestorDados,
            command=messageToRetorn['rehabilitationResults'],
            destination=msg['source']
        )
        await broker.send(sms.get_message())
    else:
        await send_problematic_message(broker, msg, "Erro ao buscar exercício de reabilitação.")


# ===================== GET =====================
async def _handle_get(broker, msg, collection, document, api, auth_api, command):
    try:
        if "user" in collection:
            command = "getUser"
            response = auth_api.get(f"/{collection}")
        elif "exercise" in collection:
            command = "getExercise"
            if 'type' in document:
                response = api.get(f"/{collection}/type/{document['type']}")
            elif 'typeOfProcessing' in document:
                response = api.get(f"/{collection}/processing/{document['typeOfProcessing']}")
            elif 'exercise' in document:
                response = api.get(f"/{collection}/{document['exercise']}")
            else:
                response = api.get(f"/{collection}")
        elif "scheduling" in collection:        #TODO: Verificar isso
            command = "getScheduling"
            if 'user' in document:
                response = api.get(f"/{collection}/user/{document['user']}")
            else:
                response = api.get(f"/{collection}")
        elif "recording" in collection:
            command = 'getRecording'
            if 'recording' in document:
                response = api.get(f"/{collection}/{document['recording']}")
            else:
                response = api.get(f"/{collection}")
        elif "result" in collection:
            command = 'getResults'
            if 'exercise' in document:
                response = api.get(f"/{collection}/exercise/{document['exercise']}")
            elif 'user' in document:
                response = api.get(f"/{collection}/user/{document['user']}")
            else:
                response = api.get(f"/{collection}/{document.get('id', '')}")
        elif "session" in collection:
            pass
        else:
            if "report" in collection:
                command = 'getReport'
                msg['source'] = None  # Send to all
            if "status" in collection:
                command = 'sendMeTheLastState'

            response = api.get(f"/{collection}")

        if response and response.status_code == 200:
            data = response.json()
            if isinstance(data, cursor.Cursor):
                data = list(data)
            sms = Message(
                message=json.dumps(data, cls=JSONEncoder),
                source=gestorDados,
                command=messageToRetorn.get(command),
                destination=msg['source']
            )
            await broker.send(sms.get_message())
        else:
            await send_not_found_message(broker, msg, document)

    except Exception as e:
        logger.exception(f"Erro em _handle_get: {e}")
        await send_problematic_message(broker, msg, "Erro ao processar GET.")


# ===================== SET =====================
async def _handle_set(broker, msg, collection, document, api, auth_api):
    response = None
    command = "setData"
    document = clean_invalid_floats(document)

    try:
        response = None
        if "exercise" in collection:
            response = api.post(f"/{collection}", json=document)
        elif "register" in collection:
            response = auth_api.post(f"/{collection}", json=document)
        elif "recording" in collection:
            command = 'sendRecordingId'
            newPath = await enviar_audio_para_backend(
                caminho_audio=document['path'],
                userName=document['userName'],
                subpasta=document['exerciseStep']
            )
            if newPath:
                document['path'] = newPath
            document = clean_invalid_floats(document)
            response = api.post(f"/{collection}", json=document)
            #if response and response.status_code in [200, 201]:
                #await deleteFile(filePath=[document['path']])  # Delete local file
             

        elif "result" in collection:
            backend_PathToChart = []
            pathToChart = document['pathToChart']
            for i, path in enumerate(pathToChart[:4]):
                newPath = await enviar_imagem_para_backend(
                    caminho_imagem=path,
                    userName=currentUser['name'],
                    subpasta=document['processing_type']
                )
                backend_PathToChart.append(newPath)
            document['pathToChart'] = backend_PathToChart
            document = clean_invalid_floats(document)
            response = api.post(f"/{collection}", json=document)
            if response and response.status_code in [200, 201]:
                await deleteFile(filePath=pathToChart)
        else:
            await send_problematic_message(broker, msg, "Coleção inválida para operação SET.")
            return

        if response and response.status_code in [200, 201]:
            data = response.json()
            sms = Message(
                message=data.get('message', 'Dados guardado com sucesso.'),
                new_values=data.get("id", ""),
                source=gestorDados,
                command=messageToRetorn[command],
                destination=msg['source']
            )
            await broker.send(sms.get_message())
        else:
            await send_problematic_message(broker, msg, f"Erro ao guardar dados: {response.text}")

    except Exception as e:
        logger.exception(f"Erro em _handle_set: {e}")
        await send_problematic_message(broker, msg, "Erro interno no SET.")


# ===================== DELETE =====================
async def _handle_delete(broker, msg, collection, document, api, auth_api):
    try:
        id_ = document.get('id', '')
        response = None
        if "user" in collection:
            response = auth_api.delete(f"/{collection}/{id_}")
        elif "status" in collection:
            response = api.delete(f"/{collection}")
        else:
            response = api.delete(f"/{collection}/{id_}")
        if response and response.status_code == 200:
            data = response.json()
            sms = Message(
                message=data.get('message', 'Dados apagados com sucesso.'),
                source=gestorDados,
                command=messageToRetorn['delete'],
                destination=msg['source']
            )
            await broker.send(sms.get_message())
        else:
            await send_problematic_message(broker, msg, f"Erro ao apagar dados: {response.text}")

    except Exception as e:
        logger.exception(f"Erro em _handle_delete: {e}")
        await send_problematic_message(broker, msg, "Erro interno no DELETE.")


# ===================== UPDATE =====================
async def _handle_update(broker, msg, collection, document, api, auth_api):
    try:
        id_ = document.get('id', '')
        payload = msg.get("new_values", {})
        if "user" in collection:
            response = auth_api.put(f"/{collection}/{id_}", json=payload)
        elif "report" in collection:
            # collection = collection.replace("report", "reports")
            response = api.put(f"/{collection}", json=payload)
        else:
            response = api.put(f"/{collection}/{id_}", json=payload)

        if response and response.status_code == 200:
            data = response.json()
            sms = Message(
                message=data.get('message', 'Dados atualizados com sucesso.'),
                source=gestorDados,
                command=messageToRetorn['update'],
                destination=msg['source']
            )
            await broker.send(sms.get_message())
        else:
            await send_problematic_message(broker, msg, f"Erro ao atualizar dados: {response.text}")

    except Exception as e:
        logger.exception(f"Erro em _handle_update: {e}")
        await send_problematic_message(broker, msg, "Erro interno no UPDATE.")


# ===================== PAUSE DIAGNOSTIC =====================
async def _handle_pause_diagnostic(broker, msg, collection, document, api):
    
    try:
        if 'audio' in document:
            document['audio'] = await convert_to_document(document["audio"])
        
        response = api.post(f"/{collection}", json=document)
        data = response.json() if response else {}

        if response and response.status_code in [200, 201]:
            sms = Message(
                message=data.get('message', 'Dados guardado com sucesso.'),
                new_values=data.get("id", ""),
                source=gestorDados,
                command=messageToRetorn['pauseDiagnostic'],
                destination=None
            )
            await broker.send(sms.get_message())
        else:
            sms = Message(
                message=data.get('message', 'Erro ao guardar dados.'),
                source=gestorDados,
                command=messageToRetorn['errorPausingDiagnostic'],
                destination=None
            )
            await broker.send(sms.get_message())

    except Exception as e:
        logger.exception(f"Erro em _handle_pause_diagnostic: {e}")
        await send_problematic_message(broker, msg, "Erro interno no PAUSE DIAGNOSTIC.")




# ============================================
# FUNÇÕES AUXILIARES
# ============================================

# async def clean_invalid_floats(obj):
#     if isinstance(obj, dict):
#         return {k: await clean_invalid_floats(v) for k, v in obj.items()}
#     if isinstance(obj, list):
#         return [await clean_invalid_floats(v) for v in obj]
#     if isinstance(obj, float):
#         if math.isnan(obj) or math.isinf(obj):
#             return 0.0  # ou None, ou string, como precisar
#     return obj

def clean_invalid_floats(obj):
    if isinstance(obj, dict):
        return {k: clean_invalid_floats(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_invalid_floats(v) for v in obj]
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            logger.warning(f"Valor float inválido encontrado ({obj}) → substituído por 0.0")
            return 0.0
    return obj


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


async def detect_collection(command):
    """Identifica a coleção correspondente a um comando."""
    command = command.lower()
    if "user" in command: return "user"
    if "register" in command: return "register"
    if "exercise" in command: return "exercise"
    if "recording" in command: return "recording"
    if "results" in command: return "result"
    if "session" in command: return "session"
    if "scheduling" in command: return "scheduling"
    if "diagnostic" in command: return "pauseAnalysis"
    if "state" in command: return "statusAnalysis"
    if "report" in command: return "report"
    return None

async def convert_to_document(message):
    """Converte a mensagem recebida para dicionário JSON."""
    try:
        #return json.loads(message) if isinstance(message, str) else message
        return safe_load_json(message)
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao converter mensagem: {e}")
        return None

async def convert_to_ObjectId(obj):
    """Converte string para ObjectId se aplicável."""
    try:
        if isinstance(obj, str):
            return ObjectId(obj)
        return obj
    except Exception as e:
        logger.error(f"Erro ao converter {obj} para ObjectId: {e}")
        return None

async def send_invalid_command(broker, msg):
    logger.warning(f"Comando inválido recebido: {msg.get('command')}")
    sms = Message(message="Instrução inválida.",
                  source=gestorDados,
                  command=messageToRetorn['problem'],
                  destination=msg['source'])
    await broker.send(sms.get_message())

async def send_problematic_message(broker, msg, error_message):
    logger.error(f"Erro de operação: {error_message}")
    sms = Message(message=error_message,
                  source=gestorDados,
                  command=messageToRetorn['problem'],
                  destination=msg['source'])
    await broker.send(sms.get_message())

async def send_not_found_message(broker, msg, query):
    if 'type' in query.keys():
        sms = Message(message=f"Nenhum dado encontrado para o tipo: {query['type']}.",
                      source=gestorDados,
                      command=messageToRetorn['notFoundType'],
                      destination=msg['source'])
    else:
        sms = Message(message="Nenhum dado encontrado.",
                      source=gestorDados,
                      command=messageToRetorn['notFound'],
                      destination=msg['source'])
    await broker.send(sms.get_message())


# ==========================
# Apaga os ficheiros locais.
# ==========================
# async def deleteFile(filePath):
#     """
#     Recebe uma lista de caminhos e tenta apagar os ficheiros.
#     Atenção: é chamada com listas na tua lógica original, mantenho isso.
#     """
#     try:
#         for file_path in filePath:
#             try:
#                 # Se o ficheiro não existir, captura FileNotFoundError
#                 os.chmod(file_path, stat.S_IWRITE)
#                 os.remove(file_path)
#                 logger.info("Ficheiro apagado: %s", file_path)
#             except FileNotFoundError:
#                 logger.warning("Ficheiro não existe: %s", file_path)
                
#             except PermissionError:
#                 logger.warning("Permissão negada ao apagar: %s", file_path)
#             except Exception as e:
#                 logger.exception("Erro ao apagar ficheiro %s: %s", file_path, e)
#     except Exception as e:
#         logger.exception("Erro geral em deleteFile: %s", e)


async def deleteFile(filePath):
    """
    Recebe uma lista de caminhos e tenta apagar os ficheiros.
    Atenção: é chamada com listas na tua lógica original, mantenho isso.
    """
    for file_path in filePath:
        try:
            # 1. Garante permissão de escrita
            try:
                os.chmod(file_path, stat.S_IWRITE)
                #os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)  # Usuário: leitura e escrita
            except Exception:
                pass

            # 2. Remove atributos de "read-only", "system", etc.
            try:
                ctypes.windll.kernel32.SetFileAttributesW(file_path, 0x80)  # FILE_ATTRIBUTE_NORMAL
            except Exception:
                pass

            # 3. Apaga
            os.remove(file_path)
            logger.info("Ficheiro apagado: %s", file_path)

        except PermissionError:
            logger.error("Permissão negada: %s — provavelmente aberto por outro processo.", file_path)

        except FileNotFoundError:
            logger.warning("Ficheiro não existe: %s", file_path)

        except Exception as e:
            logger.exception("Erro ao apagar %s: %s", file_path, e)


# ==========================
# Uploads para o backend (mantém a lógica original)
# ==========================
async def enviar_audio_para_backend(caminho_audio, userName, subpasta):
    """
    Faz upload do áudio para o backend via endpoint definido e retorna o path no backend (ou None).
    Mantive o endpoint que pediste.
    """
    url_backend = "http://localhost:5000/casa_viva/home/upload-audio"
    try:
        logger.info("Enviando áudio para backend: %s (user=%s, sub=%s)", caminho_audio, userName, subpasta)
        with open(caminho_audio, "rb") as f:
            files = {"file": f}
            data = {"userName": userName, "subpasta": subpasta}
            response = requests.post(url_backend, files=files, data=data, timeout=30)
            if response.status_code == 200:
                logger.info("Áudio enviado com sucesso.")
                # Apaga o ficheiro local (a tua lógica original fazia isso)
                await deleteFile(filePath=[caminho_audio])
                return response.json().get("path")
            else:
                logger.warning("Falha ao enviar áudio: %s", response.text)
    except Exception as e:
        logger.exception("Erro ao enviar áudio para backend: %s", e)
    return None


async def enviar_imagem_para_backend(caminho_imagem, userName, subpasta):
    """
    Faz upload de imagem para o backend e retorna path remoto (ou None).
    """
    url_backend = "http://localhost:5000/casa_viva/home/upload-imagem"
    try:
        logger.info("Enviando imagem para backend: %s (user=%s, sub=%s)", caminho_imagem, userName, subpasta)
        with open(caminho_imagem, "rb") as f:
            files = {"file": f}
            data = {"userName": userName, "subpasta": subpasta}
            response = requests.post(url_backend, files=files, data=data, timeout=30)
            if response.status_code == 200:
                logger.info("Imagem enviada com sucesso.")
                return response.json().get("path")
            else:
                logger.warning("Falha ao enviar imagem: %s", response.text)
    except Exception as e:
        logger.exception("Erro ao enviar imagem para backend: %s", e)
    return None


async def handle_crud_operations(broker, msg, command, document, collection, api, messageToRetorn):
    """
    Executa operações CRUD genéricas (GET, SET, UPDATE, DELETE) no servidor via API.
    Inclui logging, validação e envio de mensagens de retorno.
    """

    try:
        # ================== GET ==================
        if "get" in command:
            response = None

            if "exercise" in collection:
                if 'type' in document:
                    response = api.get(f"/{collection}/type/{document['type']}")
                elif 'typeOfProcessing' in document:
                    response = api.get(f"/{collection}/processing/{document['typeOfProcessing']}")
                elif 'exercise' in document:
                    response = api.get(f"/{collection}/{document['exercise']}")
                else:
                    response = api.get(f"/{collection}")

            elif "user" in collection:
                auth_api = APIClient("http://localhost:5000/casa_viva/home/auth")
                response = auth_api.get(f"/{collection}")

            elif "recording" in collection:
                if 'recording' in document:
                    response = api.get(f"/{collection}/{document['recording']}")
                else:
                    response = api.get(f"/{collection}")

            elif "result" in collection:
                if 'exercise' in document:
                    response = api.get(f"/{collection}/exercise/{document['exercise']}")
                elif 'user' in document:
                    response = api.get(f"/{collection}/user/{document['user']}")
                else:
                    response = api.get(f"/{collection}/{document.get('id', '')}")

            elif "report" in collection:
                response = api.get(f"/{collection}")
                msg['source'] = None  # broadcast

            else:
                await send_problematic_message(broker, msg, "Coleção inválida para operação GET.")
                return

            if response and response.status_code == 200:
                data = response.json()
                if isinstance(data, cursor.Cursor):
                    data = list(data)
                data = json.dumps(data, cls=JSONEncoder)
                command_key = messageToRetorn.get(command)
                sms = Message(
                    message=data,
                    source=gestorDados,
                    command=command_key or "returningData",
                    destination=msg['source']
                )
                await broker.send(sms.get_message())
            else:
                await send_not_found_message(broker, msg, document)
            return

        # ================== SET ==================
        elif "set" in command:
            response = api.post(f"/{collection}", json=document)
            if response and response.status_code in [200, 201]:
                data = response.json()
                sms = Message(
                    message=data.get('message', 'Dados guardados com sucesso.'),
                    new_values=data.get("id", ""),
                    source=gestorDados,
                    command=messageToRetorn.get(command, 'storedData'),
                    destination=msg['source']
                )
                await broker.send(sms.get_message())
            else:
                await send_problematic_message(broker, msg, f"Erro ao guardar dados: {response.text}")
            return

        # ================== DELETE ==================
        elif "delete" in command:
            response = api.delete(f"/{collection}/{document.get('id', '')}/")
            if response and response.status_code == 200:
                data = response.json()
                sms = Message(
                    message=data.get('message', 'Dados apagados com sucesso.'),
                    source=gestorDados,
                    command=messageToRetorn['delete'],
                    destination=msg['source']
                )
                await broker.send(sms.get_message())
            else:
                await send_problematic_message(broker, msg, f"Erro ao apagar dados: {response.text}")
            return

        # ================== UPDATE ==================
        elif "update" in command:
            response = api.put(f"/{collection}/{document.get('id', '')}/", json=msg.get("new_values", {}))
            if response and response.status_code == 200:
                data = response.json()
                sms = Message(
                    message=data.get('message', 'Dados atualizados com sucesso.'),
                    source=gestorDados,
                    command=messageToRetorn['update'],
                    destination=msg['source']
                )
                await broker.send(sms.get_message())
            else:
                await send_problematic_message(broker, msg, f"Erro ao atualizar dados: {response.text}")
            return

        # ================== OPERAÇÃO DESCONHECIDA ==================
        else:
            await send_invalid_command(broker, msg)

    except Exception as e:
        logging.error(f"Erro ao executar operação CRUD ({command}) em {collection}: {e}", exc_info=True)
        await send_problematic_message(broker, msg, f"Erro interno ao processar operação {command}.")


# ============================================
# MONITOR DO TECLADO
# ============================================

async def monitor_keyboard():
    """Permite reiniciar manualmente o módulo com ENTER."""
    while True:
        await aioconsole.ainput("Pressione ENTER para reiniciar...\n")
        logger.info("Reiniciando o módulo...")
        os.execl(sys.executable, sys.executable, *sys.argv)

# ============================================
# LOOP PRINCIPAL
# ============================================

async def main():
    """Loop principal do módulo gestor de dados."""
    while True:
        try:
            logger.info("Tentando conectar ao broker...")
            async with websockets.connect(urlLocal) as local_websocket:
                task1 = asyncio.create_task(handle1(local_websocket))
                task2 = asyncio.create_task(monitor_keyboard())
                await asyncio.gather(task1, task2)
        except (websockets.ConnectionClosed, ConnectionRefusedError) as e:
            logger.warning(f"Erro de conexão: {e}. Tentando reconectar em 5 segundos...")
            await asyncio.sleep(5)
        except Exception as e:
            logger.exception(f"Erro inesperado: {e}. Reiniciando módulo em 5 segundos...")
            await asyncio.sleep(5)

# ============================================
# EXECUÇÃO
# ============================================

if __name__ == "__main__":
    asyncio.run(main())
