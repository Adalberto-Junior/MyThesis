import asyncio
import websocket
import websockets
import aioconsole
import sys
import json
import requests
import threading
import time
import ssl
import logging
#from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import win32com.client as win32
import zipfile
import os
import pygame
import re

from collections import deque
from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root)+'\WebAppAssistantV2\Aplicaction')
#print(sys.path)

from modules.Message import *
from modules.moduloName import *
from modules.mmi import *


# ============================================
# CONFIGURAÇÃO DO LOGGING
# ============================================

# Ensure the log folder exists
os.makedirs("logs", exist_ok=True)

# Cria logger
logger = logging.getLogger("AssistantLogger")
logger.setLevel(logging.DEBUG)

# Formato do log
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Handler para consola
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Handler para ficheiro
file_handler = logging.FileHandler("logs/assistant.log", encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)




# Endereço do servidor WebSocket
host = "localhost" 
mmiCli_Out_add = f"wss://{host}:8005/IM/USER1/APP" #Endereço do servidor WebSocket de saída
lhost = "127.0.0.1"
#fusion_address = f"http://{host}:8000/IM/USER1/APPSPEECH"
fusion_address =  f"https://{lhost}:8000/IM/USER1/APPSPEECH"
GUI_address =  f"https://{lhost}:8000/IM/USER1/APPUI"

# 🔐 Token e nome do módulo
BROKER_NAME = assistente
BROKER_TOKEN = "token_assistente_123"


urlLocal = f"ws://{host}:8765" #Endereço do servidor WebSocket local
menu = {
         "communication_skills": "Para fazer análise podes dizer: Quero analisar as minhas capacidades de comunicação. BR. Como estão as minhas capacidades de comunicação? BR. Como está a minha comunicação?",
         "specific_exercises": "Para fazer um exercício específico podes dizer: Quero fazer exercício de [tipo de exercício. Ex: Articulação]. BR. Gostaria de fazer exercício de [tipo de exercício]. BR. Exercício de [tipo de exercício], por favor.",
         "continue_analyze": "Para fazer próximo exercício na fila podes dizer: Seguinte exercício, por favor. . BR. Próximo exercício, por favor. BR. Prossiga para o próximo. ",
         "continue_later": "Para pausar a análise e continuar depois podes dizer: Vamos continuar mais tarde. BR. Podmos continuar mais tarde? BR. Podemos fazer uma pausa e continuar mais tarde? ",
         "continue_from_lst_ste": "Para continuar de onde pareste podes dizer: Podemos continuar a análise? BR. Gostaria de continuar de onde parei. BR. Continuar do último estado, por favor.",
         "request_Diagnostic_data": "Para ver o relatório das análises escrito pelo terapeuta podes dizer: Quero ver o relatório das análises. BR. Gostaria de ver as observações do teste. BR. Há algum relatório para ver? ",
         "startRehabilitation": "Para começar o processo de reabilitação podes dizer: Quero começar a reabilitação. BR. Gostaria de iniciar o processo de reabilitação. BR. Iniciar reabilitação, por favor.",
         "show_menu": "Para ver o menu, podes dizer: Quero ver o menu. BR. Mostra o menu, por favor. BR. Quais são as funcionalidades que existem? ",
         "logout": "Para fazer o logout, podes dizer: Fazer logout. BR. Terminar a sessão, por favor. BR. logout, por favor."
       }

audioMenu=  """
             Para fazer análise podes dizer: Quero analisar as minhas capacidades de comunicação. Ou Como está a minha comunicação?
             Para fazer um exercício específico podes dizer: Quero fazer exercício de [ e diz o tipo de exercício. Ex: Articulação]. Ou Gostaria de fazer exercício de [ e diz o tipo de exercício].
             Para fazer o próximo exercício na fila podes dizer: Seguinte exercício, por favor.  Ou Próximo exercício, por favor.
             Para pausar a análise e continuar depois podes dizer: Vamos continuar mais tarde. Ou Podemos fazer uma pausa e continuar mais tarde?
             Para continuar de onde pareste podes dizer: Podemos continuar a análise? Ou Gostaria de continuar de onde parei.
             Para ver o relatório das análises escrito pelo terapeuta podes dizer: Quero ver o relatório das análises. Ou Gostaria de ver as observações do teste.
             Para começar o processo de reabilitação podes dizer: Quero começar a reabilitação. Ou Gostaria de iniciar o processo de reabilitação.
             Para fazer o logout, podes dizer: Fazer logout. Ou Terminar a sessão, por favor.
             E se quiseres ver o menu, podes dizer: Quero ver o menu. ou Mostra o menu, por favor. e eu irei dizer e mostrar na tela o menu.
            """

# Ação de acordo com o intent
intentAction = {
                "communication_skills": "fazer_o_diagnostico",
                "continue_later": "pausar_o_diagnostico",           
                "request_Diagnostic_data": "mostrar_o_diagnostico", 
                "request_change_username": "alterar_o_nome_do_utilizador", #TODO: TALVEZ NÃO SEJA NECESSÁRIO
                "ask_username": "mostrar_atual_utilizador",     #TODO: TALVEZ SEJA NECESSÁRIO PARA PODER TER A CERTEZA QUE O MESMO ESTÁ LOGADO
                "sendToTherapist": "enviar_dados",
                "continue_analyze": "continuar_a_analise",
                "continue_from_lst_ste": "continuar_o_progresso",
                "specific_exercises": "fazer_exercicio_de_tipo",
                "register" : "newUser",
                "login": "login",
                "logout": "logout",
                "addExercise": "add_exercise",
                "startRehabilitation": "comecar_reabilitacao",
            }
#Comando
comando = {
    "voz" : "toVoice",
    "projetar" : "toDisplay",
    "record": "toRecord",
    "cancel" : "cancelTheRecord",
    "analyze" : 'processTheData',
    "sair"    : 'logout',
    "apagarSt"  : 'deleteState'
    
}
#Messagem a receber
returnMessage = ['recordingStopped','readyToRecord','diagnosticPaused','nextExercise','processedData', 'noExerciseFound']

#Processamento de exercicio
filename = "../../ficheiro/exercicio.txt"
queue = deque()         #Queue para guardar os id dos exercicios
displaySms = {"message": "",
              "command": "display"}
#currentSession
session = {}
user_logged_in = asyncio.Event()

#CurrentExercise
previousExercises = []
currentExercise = {}
exerciseDic = {}
currentExerciseId = 0
currentStep = 0
lastState = False

# Lista para armazenar os exercícios de reabilitação anteriores
previousExercisesRehabilitation = []
currentExerciseRehabilitation = {}


# ==============================
# Função aprimorada para lidar com mensagens do MMI
# ==============================
async def handle_mmi(mmiServer, broker):
    global currentExercise, currentStep, currentExerciseId, lastState
    global previousExercisesRehabilitation, currentExerciseRehabilitation

    namespace = {
        "mmi": "http://www.w3.org/2008/04/mmi-arch",
        "emma": "http://www.w3.org/2003/04/emma"
    }

    logger.info("Iniciando o tratamento de mensagens do MMI...")

    async for message in mmiServer:
        if not message or message in ("RENEW", "OK"):
            logger.info(f"MMI Message ignorada: {message}")
            continue

        logger.info(f"📩 Mensagem recebida do MMI: {message}")

        try:
            # ------------------------------
            # 1️⃣ Parse XML EMMA e extrair conteúdo
            # ------------------------------
            root = ET.fromstring(message)
            interpretation = root.find(".//emma:interpretation", namespace)
            content = (
                interpretation.find("command").text.strip()
                if interpretation is not None and interpretation.find("command") is not None
                else ""
            )

            if not isinstance(content, str):
                logger.warning(f"⚠️ Tipo inválido em 'content': {type(content)}")
                continue

            data = safe_load_json(content)
            intent = data["nlu"]["intent"]
            logger.info(f"🎯 Intent detectado: {intent}")

            # ------------------------------
            # 2️⃣ Caso: LOGIN / REGISTER
            # ------------------------------
            if intent in ("register", "login") and not user_logged_in.is_set():
                await send_to_broker(
                    broker,
                    message=data["data"],
                    intent=intent,
                    destination=gestorDados
                )
                continue

            # ------------------------------
            # 3️⃣ Verifica se usuário está logado
            # ------------------------------
            if not user_logged_in.is_set():
                await sendToVoice("Para usar o sistema, é necessário fazer login primeiro.")
                logger.warning("⚠️ Nenhum utilizador logado. Ignorando mensagem.")
                continue

            # ------------------------------
            # 4️⃣ Tratamento de intents logados
            # ------------------------------
            if intent in ("communication_skills", "continue_analyze", "continue_from_lst_ste"):
                if intent == "continue_from_lst_ste":
                    lastState = True

                await send_to_broker(
                    broker,
                    message=data["nlu"]["message"],
                    intent=intent,
                    destination=diagnosticoM
                )

            elif intent == "startRehabilitation":
                logger.info("🧠 Iniciando processo de reabilitação...")
                
                await send_to_broker(
                    broker,
                    message=data["nlu"]["message"],
                    intent=intent,
                    destination=exercicioM
                )

            elif intent == "show_menu":
                displaySms["message"] = menu
                displaySms["command"] = "menu"
                await sendToGui(json.dumps(displaySms))

                displaySms["command"] = "display"
                await sendToVoice(audioMenu)

            elif intent == "specific_exercises":
                await send_to_broker(
                    broker,
                    message=data["nlu"]["type"],
                    intent=intent,
                    destination=diagnosticoM
                )

            elif intent == "request_Diagnostic_data":
                await send_to_broker(
                    broker,
                    message=data["nlu"]["message"],
                    intent=intent,
                    destination=diagnosticoM
                )

            elif intent == "continue_later":
                await handle_pause_intent(broker, data)

            elif intent == "sendToTherapist":
                await handle_send_to_therapist()

            elif intent == "logout":
                await send_to_broker(
                    broker,
                    message=json.dumps(data["nlu"]["message"]),
                    intent=intent,
                    destination=gestorDados
                )


            else:
                logger.warning(f"❓ Intent desconhecido: {intent}")
                
                await sendToVoice(f"Desculpe, não reconheço esse comando. Intent desconhecido: {intent}.")
                

        except Exception as e:
            logger.error(f"❌ Erro ao processar mensagem: {e}")


# ==============================
# Funções auxiliares para modularizar o código
# ==============================
async def send_to_broker(broker, message, intent, destination, source=assistente):
    """Envia uma mensagem formatada ao broker."""
    command = intentAction.get(intent)
    if not command:
        logger.warning(f"⚠️ Intent '{intent}' sem comando associado.")
        return

    sms = Message(message=message, source=source, command=command, destination=destination)
    await broker.send(sms.get_message())
    logger.info(f"✅ Mensagem enviada ao broker → {destination} | comando: {command}")


async def handle_pause_intent(broker, data):
    """Trata o pedido de pausa do diagnóstico."""
    intent = data["nlu"]["intent"]
    if currentExercise:
        sms_data = {
            "exercise": currentExercise["_id"],
            "currentStep": currentStep,
            "user": session["userId"],
            "state": "middle",
        }
        await send_to_broker(
            broker,
            message=json.dumps(sms_data),
            intent=intent,
            destination=diagnosticoM
        )
    else:
        await send_to_broker(
            broker,
            message="Pausar os exercícios!",
            intent=intent,
            destination=exercicioM
        )


async def handle_send_to_therapist():
    """Envia e-mail com resultados ao terapeuta."""
    logger.info("📧 Enviando relatório ao terapeuta...")
    

    subject = f"Resultados da análise da utente {session['name']}"
    destination = session["email_therapist"]

    body = f"""
    <p>Bom dia, {session['therapist']}, espero que esteja bem.</p> 
    <p>Envio este email para partilhar <b>os resultados da última análise das capacidades comunicativas da utente {session['name']}.</b></p>
    <p><b>Em anexo envio um ficheiro com os gráficos. Para ver os dados numéricos, aceda ao site e consulte os resultados da utente.</b></p>
    <p>Em caso de dúvidas, por favor, entre em contacto com {session['name']}.</p>
    <p>Com os melhores cumprimentos,</p>
    <p>Casa Viva</p>
    """

    # Gera o zip com os gráficos
    pasta = r"..\Grafico"
    ficheiros = [
        os.path.join(raiz, arquivo)
        for raiz, _, arquivos in os.walk(pasta)
        for arquivo in arquivos
    ]
    caminho_zip = os.path.join(pasta, "Grafico.zip")

    await zipar_ficheiros(caminho_zip, ficheiros)

    attachment = (
        r"..\..\WebAppAssistantV2\Grafico\Grafico.zip"
    )

    await sendToTherapistEmail(destination, subject, body, attachment)
    logger.info("✅ Email enviado com sucesso.")
    



# =====================================================
# Função principal de processamento de mensagens do Broker
# =====================================================
async def handle_broker(mmiServer, broker):
    global session, currentExercise, currentStep, currentExerciseId, previousExercises, lastState
    global previousExercisesRehabilitation, currentExerciseRehabilitation
  
    # 🔑 Envia credenciais logo após conectar
    # auth_payload = json.dumps({
    #     "name": BROKER_NAME,
    #     "token": BROKER_TOKEN
    # })
    logger.info("Enviando credenciais de autenticação ao broker.")

    auth_payload = json.dumps({"auth": {"name": BROKER_NAME, "token": BROKER_TOKEN}})

    await broker.send(auth_payload)

    # 🕵️‍♂️ Aguarda resposta do servidor
    auth_response = await broker.recv()
    logger.info("Resposta de autenticação recebida do broker.")
    if auth_response:
        try:
            auth_data = safe_load_json(auth_response)
        except json.JSONDecodeError:
            logger.warning(f"⚠️ Erro: resposta de autenticação inválida: {auth_response}")
            return

        if auth_data.get("status") != "authenticated":
            logger.error(f"❌ Falha na autenticação: {auth_data}")
            await broker.close()
            return

        logger.info(f"🔐 Autenticação bem-sucedida: {auth_data}")
        greeting = (
                "Olá, meu caro utilizador! BR. "
                "Se precisares de ajuda, estou cá. BR. "
                "Antes de usares o sistema, lembra-te de fazer o login. BR. "
                "Se acabaste de iniciar, espera eu carregar todos os módulos. Aviso-te quando estiver pronto."
            )
        await sendToVoice(greeting.replace(" BR. ", "\n"))
        displaySms["message"] = greeting.replace(" BR. ", "")
        await sendToGui(json.dumps(displaySms))

    async for message in broker:
        logger.info(f"\n📩 [Broker] Mensagem recebida:\n{message}\n")


            

        # Processamento normal
        try:
            messag = safe_load_json(message)

            # Se o resultado ainda for uma string, tentar decodificar de novo
            # if isinstance(messag, str):
            #     logger.debug("Mensagem estava duplamente codificada — decodificando novamente.")
            #     messag = json.loads(messag)

            # logger.debug(f"Mensagem decodificada final: {messag}, tipo: {type(messag)}")
            cmd = messag.get("command", "")
            msg_content = messag.get("message", "")

            # ======================== SISTEMA ========================
            if cmd == "weCanStart":
                await sendToVoice("Já podes fazer o login, tenho tudo pronto para iniciarmos.")

            elif cmd == "readyToRecord":
                await handle_ready_to_record(broker)

            elif cmd == "nextExercise":
                await handle_next_exercise(broker)

            elif cmd == "diagnosticPaused":
                await handle_diagnostic_paused()

            elif cmd == "errorPausingDiag":
                await send_both("Aconteceu um erro ao pausar a análise. Tenta novamente dizendo: Vamos continuar depois.")

            elif cmd == "processedData":
                await send_both("Já terminei de analisar os dados. Se quiseres continuar, diga: Próximo exercício, por favor.")

            elif cmd == "currentStep":
                currentStep = safe_load_json(msg_content)

            elif cmd in {"registed", "loginfailed", "loggedIn"}:
                await handle_auth_responses(cmd, msg_content)

            elif cmd == "currentSession":
                await handle_current_session(msg_content)

            elif cmd in {"noExerciseFound", "theExercisesAreFinished", "ExerciseError"} or \
                any(k in cmd for k in ["error", "failed"]):
                await send_both(msg_content)

            elif cmd == "sendingExercise":
                currentExercise = safe_load_json(msg_content)
                previousExercises.append(safe_load_json(msg_content))

            elif cmd == "sendingRehabilitationExercise":
                currentExerciseRehabilitation = safe_load_json(msg_content)
                previousExercisesRehabilitation.append(safe_load_json(msg_content))
                await handle_rehabilitation_exercise()

            elif cmd == "returningReport":
                await handle_returning_report(broker, msg_content)

            elif cmd == "logout":
                await handle_logout(msg_content)

            else:
                if cmd == "confirmation":
                    logger.info("✅ Mensagem de confirmação recebida.")
                else:
                    logger.warning(f"⚠️ Comando desconhecido recebido: {cmd}. Mensagem: {msg_content}")
                #await broker.send(Message(message="recebido", source=assistente, command="confirmation", destination="").get_message())

        except json.JSONDecodeError:
            logger.error("❌ Erro ao decodificar JSON.")
            
        except Exception as e:
            logger.exception(f"Detalhes do erro: {e}")
            logger.warning(f"⚠️ Erro ao processar mensagem: Mensagem bruta: {message}")


# =====================================================
# Sub-funções auxiliares
# =====================================================

async def send_both(text):
    """Mostra mensagem na tela e fala"""

    logger.info(f"Mostrando e falando a mensagem: {text}")

    displaySms["message"] = text
    await sendToGui(json.dumps(displaySms))

    # Substitui "BR." com quebra de linha e remove "PG."
    text = re.sub(r'\s?BR\.\s?', '\n', text)
    text = re.sub(r'\s?PG\.\s?', '', text)

    logger.info(f"Texto para voz: {text}")

    # Chama a função assíncrona
    await sendToVoice(text)



async def handle_ready_to_record(broker):
    """Processa o início de um exercício"""
    global currentExercise, currentExerciseId, lastState
    logger.info("Processando início de um exercício")

    if not currentExercise:
        await send_both("No momento não temos exercício na base de dados.")
        sms = Message(
            message="We currently do not have exercises to make a diagnostic",
            source=assistente, command=comando["cancel"], destination=diagnosticoM
        )
        await broker.send(sms.get_message())
        return

    pygame.mixer.init()

    desc_gui = f"BR. Descrição: {currentExercise.get('description', '')}," if currentExercise.get("description") else ""
    desc_audio = f"\nDescrição: {currentExercise.get('description', '')}," if currentExercise.get("description") else ""

    is_first = currentExerciseId == 0
    template_key = (is_first, lastState)
    templates = {
        (True, False): ("PG. Certo, Vamos fazer a análise das suas capacidades de comunicação. Para fazer a análise vamos começar com {type}.", "Certo, Vamos fazer a análise das suas capacidades de comunicação. Para fazer a análise vamos começar com {type}."),
        (True, True): ("PG. Vamos continuar a análise, paramos no exercício {type}.", "Vamos continuar a análise, paramos no exercício {type}."),
        (False, False): ("Agora vamos fazer o exercício {type}.", "Agora vamos fazer o exercício {type}."),
        (False, True): ("PG. Vamos continuar a análise, paramos no exercício {type}.", "Vamos continuar a análise, paramos no exercício {type}."),
    }

    intro_gui, intro_audio = [t.format(type=currentExercise["type"]) for t in templates[template_key]]

    sms = f"{intro_gui} BR. Nome do exercício: {currentExercise['name']} {desc_gui} BR. PG. Começaremos dentro de 10 segundos."
    audioSms = f"{intro_audio}\nNome do exercício: {currentExercise['name']},{desc_audio}\nComeçaremos dentro de 10 segundos."

    await send_both(sms)
    # await sendToVoice(audioSms)

    await asyncio.sleep(15)
    pygame.mixer.music.load("../Audio_util/cnt_10_segund.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    await processingDiagnostic(broker=broker, sms="Start:", cmd=comando["record"], module=diagnosticoM)


async def handle_next_exercise(broker):
    """Processa o próximo exercício"""
    global currentExercise, previousExercises, currentExerciseId, lastState, currentStep
    logger.info("Processando próximo exercício")

    if currentExercise:
        await processingDiagnostic(broker=broker, sms="we are in exercise:", cmd=comando["record"], module=diagnosticoM)
    else:
        sms = (
            f"Já terminamos todos os exercícios do tipo {previousExercises[currentExerciseId]['type']}."
            " Agora irei analisar os dados! Poderá demorar um pouco, aviso-te quando terminar."
        )
        await send_both(sms)
        msg = Message(message="There are no more exercises to do", source=assistente,
                      command=comando["analyze"], destination=diagnosticoM)
        await broker.send(msg.get_message())

        currentExerciseId += 1
        currentStep = 0

        if lastState:
            payload = json.dumps({"user": session["userId"]})
            msg = Message(message=payload, source=assistente, command=comando["apagarSt"], destination=gestorDados)
            await broker.send(msg.get_message())
            lastState = False


async def handle_diagnostic_paused():
    await send_both(
        "Análise pausada com sucesso. BR. Quando quiseres continuar, diga: Gostaria de continuar de onde parei."
    )
    currentExercise.clear()


async def handle_auth_responses(cmd, message):
    """Trata respostas de login e registro"""
    logger.info(f"Resposta de autenticação recebida: cmd={cmd}, message={message}")

    displaySms["message"] = message
    if cmd == "registed":
        await send_both(message)
    elif cmd == "loggedIn":
        displaySms.update({"status": "success", "command": "loginResult"})
        await sendToGui(json.dumps(displaySms))
    elif cmd == "loginfailed":
        displaySms.update({"status": "error", "command": "loginResult"})
        await send_both(message)


async def handle_current_session(message):
    global session
    session = safe_load_json(message)
    if not session:
        logger.error("❌ Erro ao carregar sessão atual: dados inválidos.")
        return
    
    logger.info(f"✅ Sessão iniciada: {session}")
    

    displaySms.update({"command": "userName", "message": session["name"]})
    await sendToGui(json.dumps(displaySms))

    await sendToVoice(
        f"Olá {session['name']}, seja bem-vindo! BR. "
        "As funcionalidades e as palavras-chave para usá-las estão na tela. BR. "
        "Para ouvi-las, diga: Quero ver o menu."
    )

    displaySms.update({"command": "menu", "message": menu})
    await sendToGui(json.dumps(displaySms))
    displaySms.update({"command": "display"})
    user_logged_in.set()


async def handle_rehabilitation_exercise():
    """Inicia processo de reabilitação"""

    global currentExerciseRehabilitation, previousExercisesRehabilitation
    logger.info("Iniciando processo de reabilitação")
    if not currentExerciseRehabilitation:
        return

    ex = currentExerciseRehabilitation
    sms = (
        f"Vamos começar o processo de reabilitação. BR. "
        f"Exercício de {ex['category']}. BR. Nome: {ex['title']} BR. "
        f"Objetivo: {ex['objective']} BR. Descrição: {ex['description']} BR. "
        f"Duração: {ex['duration']} minuto(s) BR. Repetições: {ex['repetitions']} vez(es) BR. "
        f"Dificuldade: {ex['difficulty']}"
    )

    displaySms.update({"command": "display"})
    audioSms = sms.replace("BR.", "")
    await send_both(sms)
    await asyncio.sleep(25)
    await sendToVoice("Iremos começar dentro de 10 segundos. Por favor, esteja preparado.")

    pygame.mixer.init()
    pygame.mixer.music.load("../Audio_util/cnt_10_segund.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    await processingRehabilitationData()


async def handle_returning_report(broker, message):
    """Processa o relatório retornado"""
    logger.info("Processando relatório retornado")
    
    report = safe_load_json(message)
    if not report:
        await send_both("Ainda não existe nenhuma observação para mostrar.")
        return
    await send_both("Aqui estão os dados do relatório com as observações das análises feitas pela terapeuta.")

    query = {str(r["_id"]): int(r["views"]) + 1 for r in report if "_id" in r and "views" in r}
    displaySms.update({"command": "report", "message": report})

    await sendToGui(json.dumps(displaySms))

    msg = Message(message=json.dumps(query), new_values = json.dumps(query), source=assistente, command="updateReport", destination=gestorDados)

    await broker.send(msg.get_message())

    displaySms.update({"command": "display"})


async def handle_logout(message):
    """Processa o logout do utilizador"""
    global session, currentExercise
    logger.info("Processando logout do utilizador")

    success = "sucesso" in message
    displaySms.update({
        "command": "logout",
        "status": "success" if success else "error",
        "message": "Terminando a Sessão" if success else "Falha ao terminar a Sessão"
    })
    await sendToGui(json.dumps(displaySms))
    await sendToVoice(message)
    if success:
        session.clear()
        currentExercise.clear()
        user_logged_in.clear()


# =====================================================
# PROCESSAMENTO DE EXERCÍCIOS
# =====================================================
async def processingDiagnostic(broker, sms, cmd, module):
    
    global currentStep
    logger.info("Processando diagnóstico")

    step = currentExercise["steps"].pop(0)
    currentStep += 1

    displaySms["command"] = "display"

    msg, audioMsg = build_exercise_step_message(step, currentExercise["type"])
    displaySms["message"] = msg
    await sendToGui(json.dumps(displaySms))
    await sendToVoice(audioMsg + "BR. Quando ouvires começar, podes começar. A gravação terminará após 5 segundos de silêncio.")

    await asyncio.sleep(20 if "leitura" in currentExercise["type"].lower() else 10)
    if not currentExercise["steps"]:
        currentExercise.clear()
        currentStep = 0

    msg_obj = Message(message=f"{sms}{currentStep}", source=assistente, command=cmd, destination=module)
    await broker.send(msg_obj.get_message())


def build_exercise_step_message(step, exercise_type):
    """Constrói as mensagens (GUI + áudio) para cada tipo de exercício"""
    logger.info(f"Construindo mensagem para o passo do exercício: {step}, tipo: {exercise_type}")

    lower_type = exercise_type.lower()
    if "palavras" in lower_type or "frases" in lower_type:
        msg = f"{step['description']}: {step.get('word', step.get('sentence',''))} BR."
        audio = f"{step['description']}: {step.get('word', step.get('sentence',''))}\n"
    elif "leitura" in lower_type:
        msg = f"{step['description']}: BR. {step['title']} BR. {step['text']}. BR."
        audio = f"{step['description']}:\n{step['title']}\n{step['text']},\n"
    elif "diadococinésia" in lower_type:
        msg = f"{step['description']}: BR. {step['syllables']}. BR."
        audio = f"{step['description']}: {step['syllables']},\n"
    elif "discurso" in lower_type:
        msg = f"{step['description']}: BR. {step['question']}, BR."
        audio = f"{step['description']}: {step['question']},\n"
    else:
        msg = "".join(f"{k}:{v}. " for k, v in step.items())
        audio = msg.replace("BR.", "")
    return msg, audio


async def processingRehabilitationData():

    logger.info("Processando dados de reabilitação")
    if currentExerciseRehabilitation.get("images"):
        displaySms["images"] = currentExerciseRehabilitation["images"]
    if currentExerciseRehabilitation.get("audios"):
        displaySms["audios"] = currentExerciseRehabilitation["audios"]
    if currentExerciseRehabilitation.get("videos"):
        displaySms["videos"] = currentExerciseRehabilitation["videos"]

    step = currentExerciseRehabilitation["steps"].pop(0)
    msg = f"Instrução: {step['instruction']}. BR."
    audioMsg = f"Instrução: {step['instruction']}.\n"

    displaySms["command"] = "rehabilitation"
    displaySms["message"] = msg
    await sendToGui(json.dumps(displaySms))
    await sendToVoice(audioMsg + "BR. Quando terminares, diga: Próximo passo, por favor.")

    if not currentExerciseRehabilitation["steps"]:
        currentExerciseRehabilitation.clear()

    displaySms["command"] = "display"


#Zipar ficheiro
async def zipar_ficheiros(caminho_zip, ficheiros):
    logger.info(f"Zipando ficheiros para: {caminho_zip}")
    try:
        with zipfile.ZipFile(caminho_zip, 'w') as zipf:
            for ficheiro in ficheiros:
                zipf.write(ficheiro, os.path.basename(ficheiro))
    except Exception as e:
        logger.error(f"Erro ao Zipar o ficheiro: {e}")

async def sendToTherapistEmail(destination, subject, body, attachment = None):
    try:
        outlook = win32.Dispatch('outlook.application')
        email = outlook.CreateItem(0)
        email.To = destination
        email.Subject = subject
        email.HTMLBody = body
        
        if attachment != None:
            email.Attachments.Add(attachment)

        email.Send()
        logger.info("Email enviado!")

    except Exception as e:
        logger.error(f"Erro ao enviar email: {e}")

# =====================================================
# Funções Auxiliares
# =====================================================
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


# 🧠 Função de monitoramento do teclado
async def monitor_keyboard():
    """Permite reiniciar o sistema pressionando ENTER."""
    while True:
        await aioconsole.ainput("Pressione ENTER para reiniciar...\n")
        logger.info("🔁 Reiniciando o assistente...")
        os.execl(sys.executable, sys.executable, *sys.argv)


# 🚀 Função principal
async def main():
    """Conecta o assistente aos servidores e mantém reconexões automáticas."""
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    try:
        ssl_context.load_cert_chain(certfile="../cert.pem", keyfile="../key.pem")
    except FileNotFoundError:
        print("⚠️  Certificados não encontrados. Continuando sem SSL verificado.")
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
    else:
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

    while True:
        try:
            logger.info("🌐 Tentando conectar aos servidores...")

            async with websockets.connect(mmiCli_Out_add, ssl=ssl_context) as mmi_ws, \
                       websockets.connect(urlLocal) as broker_ws:
                
                logger.info("✅ Conectado com sucesso aos dois servidores!")

                # Criação das tarefas paralelas
                tasks = [
                    asyncio.create_task(handle_mmi(mmi_ws, broker_ws)),
                    asyncio.create_task(handle_broker(mmi_ws, broker_ws)),
                    asyncio.create_task(monitor_keyboard())
                ]

                # Aguardar até que uma das tarefas finalize
                done, pending = await asyncio.wait(
                    tasks, return_when=asyncio.FIRST_EXCEPTION
                )

                # Cancelar tarefas restantes se uma falhar
                for task in pending:
                    task.cancel()

                # Relevantar exceção se alguma ocorreu
                for task in done:
                    if task.exception():
                        raise task.exception()

        except (websockets.ConnectionClosed, ConnectionRefusedError) as e:
            logger.warning(f"⚠️  Erro de conexão: {e}. Tentando reconectar em 5 segundos...")
            await asyncio.sleep(5)

        except Exception as e:
            logger.error(f"❌ Erro inesperado: {e}. Reiniciando em 5 segundos...")
            await asyncio.sleep(5)



async def sendToVoice(texto):

    texto = re.sub(r'\s?BR\.\s?', ' ', texto)
    texto = re.sub(r'\s?PG\.\s?', '', texto)

    result = f"""<mmi:mmi xmlns:mmi="http://www.w3.org/2008/04/mmi-arch" mmi:version="1.0">
    <mmi:startRequest mmi:context="ctx-1" mmi:requestId="text-1" mmi:source="APPSPEECH" mmi:target="IM">
        <mmi:data>
        <emma:emma xmlns:emma="http://www.w3.org/2003/04/emma" emma:version="1.0">
            <emma:interpretation emma:confidence="1" emma:id="text-" emma:medium="text" emma:mode="command" emma:start="0">
            <command>"&lt;speak version=\"1.0\" xmlns=\"http://www.w3.org/2001/10/synthesis\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://www.w3.org/2001/10/synthesis http://www.w3.org/TR/speech-synthesis/synthesis.xsd\" xml:lang=\"pt-PT\"&gt;&lt;p&gt;{texto}&lt;/p&gt;&lt;/speak&gt;"</command>
            </emma:interpretation>
        </emma:emma>
        </mmi:data>
    </mmi:startRequest>
    </mmi:mmi>"""

    mmicli = MMIClient(fusion_address,False) #Instancia o cliente MMI
    
    mmicli.sendToIm(result)

async def sendToGui(texto):
    
    result = f"""<mmi:mmi xmlns:mmi="http://www.w3.org/2008/04/mmi-arch" mmi:version="1.0">
                    <mmi:startRequest mmi:context="ctx-1" mmi:requestId="text-1" mmi:source="APPUI" mmi:target="IM">
                        <mmi:data>
                        <emma:emma xmlns:emma="http://www.w3.org/2003/04/emma" emma:version="1.0">
                            <emma:interpretation emma:confidence="1" emma:id="text-" emma:medium="text" emma:mode="command" emma:start="0">
                            <command>{texto}</command>
                            </emma:interpretation>
                        </emma:emma>
                        </mmi:data>
                    </mmi:startRequest>
                </mmi:mmi>"""
    mmicli = MMIClient(GUI_address,False) #Instancia o cliente MMI
    mmicli.sendToIm(result)


if __name__ == "__main__":

    asyncio.run(main())


