#==================================================================================================
#==================================================================================================
# Project: Assistant to speech Therapy
# File: userManager.py
# Created by: Adalberto Jr
# Created date: 24/03/2025
# Version: 1.0
# Python: 3.10
# Local: Universidade de Aveiro
# Description: This module is responsible for creating and managing users.
# ================================================================================================
#=================================================================================================
#Imports:
import asyncio
import os
import aioconsole
import base64
import websockets
import json
import bcrypt
import re
from datetime import date
from datetime import datetime
#from bson import ObjectId
from pathlib import Path
import sys
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root)+'\WebAppAssistantV2\Aplicaction')

from modules.Message import *
from modules.collectionName import *
from modules.CreatDocumentToDB import *
from modules.moduloName import *

# Endereço do servidor WebSocket
host = "localhost"
urlLocal = f"ws://{host}:8765" #Endereço do broker local

loginData = {}
session = {}
currentSession = {}

commandRecive = ['newUser', 'login', 'logout']
messageToRetorn = {
    'loginIn' : 'loggedIn',
    'failed' : 'loginfailed',
    'newUser': 'registed',
    'getout' : 'logout',
    'currentUser': 'currentSession',
    'logout': 'logout_'
}

async def handle (broker):
    async for message in broker:
        #print("broker Message:\n",message)

        if "Seu ID é" in message:
            firstSms = message
            my_id = firstSms.split()[-1]
            print(f"Meu ID é {my_id}")
            sms = f"My name is: {utilizadorM}"
            await broker.send(sms)
        else:
            try:
                messag = json.loads(message)
                print("Mensagem recebida: ", messag)

                if messag['command'] == "newUser":
                    #userData = json.loads(messag['message'])
                    userData = messag['message']
                    password = await hash_password(userData['password'])
                    #if not await verificar_hash(userData['password']):
                    #    password = hash_password(userData['password'])

                    document = CreatDocumentToDB()
                    doc = document.userDocument(name=userData['name'], age=userData['age'], email=userData['email'], password=password, therapist=userData['therapist'], email_therapist=userData['email_therapist'])
                    sms = Message(source=utilizadorM, message=doc, command="setUser", destination=gestorDados)
                    await broker.send(sms.get_message())
                    #TODO: Se estiver tudo certo enviar notificação para o assistente dizendo que o user foi adicionado com sucesso

                elif messag['command'] == "login":
                    data = messag['message']
                    loginData = data    #Wil be used other time

                    query = {'email':data['email']}
                    print(f"QUERY: {query}; type: {type(query)}")
                    sms = Message(source=utilizadorM, message=json.dumps(query) , command="getUser", destination=gestorDados)
                    await broker.send(sms.get_message())
                
                elif messag['command'] == "retorningUser":
                    result = json.loads(messag['message']) if messag['message'] else None

                    if result:
                        if result['email'] == loginData['email']:
                            if await verify_password(password=loginData['password'], hashed= result['password']):
                                print("*Palavra passe está correta")
                                sms = Message(source=utilizadorM, message="User can do login!", command=messageToRetorn['loginIn'], destination=assistente)
                                await broker.send(sms.get_message())

                                #SESSÃO:
                                today = datetime.now().strftime('%d-%m-%Y')
                                date_hour = datetime.now()
                                hour = date_hour.strftime('%H:%M:%S')
                                print(hour)

                                document = CreatDocumentToDB()
                                doc = document.sessionDocument(date=today,start=hour,end=None,user=result['_id'])
                                currentSession = json.loads(doc)
                                sms = Message(source=utilizadorM, message=doc, command="setSession", destination=gestorDados)
                                await broker.send(sms.get_message())

                                currentUser = document.curentUserDocument(userId=result['_id'],name=result['name'],email=result['email'],age=result['age'],therapist=result['therapist'],email_therapist=result['email_therapist'])
                                session = json.loads(currentUser)
                                sms = Message(source=utilizadorM, message=currentUser, command=messageToRetorn['currentUser'], destination=None)
                                await broker.send(sms.get_message())

                            else:
                                print("*Palavra passe está incorreta")
                                sms = Message(source=utilizadorM, message="A palavra passe está incorreta!", command=messageToRetorn['failed'], destination=assistente)
                                await broker.send(sms.get_message())
                        else:
                            print("*Email está incorreta")
                            sms = Message(source=utilizadorM, message="Email está incorreto!", command=messageToRetorn['failed'], destination=assistente)
                            await broker.send(sms.get_message())
                    else:
                        print("*Utilizador não encontrado")
                        sms = Message(source=utilizadorM, message="Utilizador inexistente!", command=messageToRetorn['failed'], destination=assistente)
                        await broker.send(sms.get_message())
                elif messag['command'] == "thereIsNoData":
                    print("*Nenhum utilizador encontrado.*")
                    sms = Message(source=utilizadorM, message="Nenhum utilizador encontrado.", command=messageToRetorn['failed'], destination=assistente)
                    await broker.send(sms.get_message())
                elif messag['command'] == "storedData":
                    sms = Message(source=utilizadorM, message="Login Efetuado com Sucesso!", command=messageToRetorn['newUser'], destination=assistente)
                    await broker.send(sms.get_message())
                    #TODO: ENVIAR DE ACORDO COM AS MENSAGENS
                elif messag['command'] == "UserRegistered":
                    sms = Message(source=utilizadorM, message="Utilizador registado com sucesso!", command=messageToRetorn['newUser'], destination=assistente)
                    await broker.send(sms.get_message())
                
                elif messag['command'] == "logout":
                    date_hour = datetime.now()
                    hour = date_hour.strftime('%H:%M:%S')
                    query = [{'date':currentSession['date']},{'start':currentSession['start']},{'user':currentSession['user']}]
                    new_values = {'end':hour}

                    print(f"QUERY: {query}; type: {type(query)}")
                    sms = Message(source=utilizadorM, message=json.dumps(query) , command=messageToRetorn['logout'], new_values=json.dumps(new_values), destination=gestorDados)
                    await broker.send(sms.get_message())
                    #TODO: Agora criar condição no dataManager plidar com o logout 'logout', e retornar um tipo de mensagem especifica para indicar que foi um sucesso DONE
                    #TODO: se foi sucesso, apagar fazer clear do currentsesion e de session e enviar mensagem de logout para todos para apagarem a currentSiddon deles\
                    #TODO: Alterar o Diagnostico para apenas permitir fazer o diagnostico e outras atividades caso o user esteja logado.
                    # TODO: Depois pensar como será feito o gui e o formulário para os exercicios, estudar a tese para dividir os exercícios em tipos
                elif messag['command'] == "getout":
                    if 'sucesso' in messag['message']:
                        currentSession.clear()
                        session.clear()
                        sms = Message(source=utilizadorM, message='Logout feito com sucesso', command=messageToRetorn['getout'], destination=None)
                        await broker.send(sms.get_message())
                    else:
                        sms = Message(source=utilizadorM, message='Erro ao fazer logout', command=messageToRetorn['getout'], destination=assistente)
                        await broker.send(sms.get_message())

            except json.JSONDecodeError as e:
                print(f"Erro ao decodificar mensagem: {e}")
            except Exception as e:
                print(f"Erro ao processar mensagem: {e}")

async def verificar_hash(password):
    if re.match(r'^[a-fA-F0-9]{32,128}$', password):  # Hash típico em hexadecimal
        return True
    return False

async def verificar_email(email):
    if re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
        return True
    return False

async def hash_password(password):
    salt = bcrypt.gensalt()  # salt
    hashed = bcrypt.hashpw(password.encode(), salt)
    hashed = base64.b64encode(hashed).decode('utf-8')
    return hashed

async def verify_password(password, hashed):
    if isinstance(hashed, str):
        hashed = hashed.encode()  # Codifica para bytes
    
    return bcrypt.checkpw(password.encode(), base64.b64decode(hashed))

async def monitor_keyboard():
    while True:
        await aioconsole.ainput("Pressione ENTER para reiniciar...\n")
        print("Reiniciando...")
        os.execl(sys.executable, sys.executable, *sys.argv)

async def main (): 
     while True:  # Mantém o modulo rodando indefinidamente
        try:
            print("Tentando conectar ao broker...")
            async with websockets.connect(urlLocal) as local_websocket:
                await handle(local_websocket)

                task1 = asyncio.create_task(handle(local_websocket))
                task2 = asyncio.create_task(monitor_keyboard()) #monitorar o teclado
                
                # Espera ambas as tarefas finalizarem
                await asyncio.gather(task1, task2)

        except (websockets.ConnectionClosed, ConnectionRefusedError) as e:
            print(f"Erro de conexão: {e}. Tentando reconectar em 5 segundos...")
            await asyncio.sleep(5)  # Espera antes de tentar reconectar

        except Exception as e:
            print(f"Erro inesperado: {e}. Reiniciando o modulo de gestor de utilizador em 5 segundos...")
            await asyncio.sleep(5)



if __name__ == "__main__":
    asyncio.run(main()) 

