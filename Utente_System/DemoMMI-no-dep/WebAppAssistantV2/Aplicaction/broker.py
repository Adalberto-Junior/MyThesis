
import asyncio
import websockets
import json
import logging
from datetime import datetime
import os

# ============================================================
# 🌐 SERVIDOR WEBSOCKET CENTRAL (versão com LOGS e AUTENTICAÇÃO)
# ============================================================
# Este servidor atua como um "broker" intermediário entre os
# módulos do sistema (Assistente, Gestores, GUI, etc.).
# Ele:
#   - Aceita conexões WebSocket.
#   - Identifica os clientes pelo nome enviado.
#   - Redireciona mensagens entre os módulos.
#   - Permite broadcast (mensagens sem destino específico).
# ============================================================

# Ensure the log folder exists
os.makedirs("logs", exist_ok=True)

# Configuração do logging (cria logs no console e em arquivo)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/broker_server.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# # Dicionário global para armazenar conexões ativas (client_id → websocket)
# connected_clients = {}



# Dicionário global com conexões ativas: client_id → websocket
connected_clients = {}

# # Módulos esperados e seus IDs de conexão
# client_names = {
#     "Assistant": 0,
#     "Recorder": 0,
#     "DiagnosticManager": 0,
#     "UserManager": 0,
#     "ExercisesManager": 0,
#     "DataManager": 0,
#     "VideoManager": 0,
#     "GUI": 0,
# }
# Tabela de nomes conhecidos dos módulos e seus IDs de conexão
client_names = {
    "Assistant": 0,            # Assistente
    "Recorder": 0,             # Gravador de Áudio
    "DiagnosticManager": 0,    # Diagnóstico
    "UserManager": 0,          # Gestor de Utilizadores
    "ExercisesManager": 0,     # Gestor de Exercícios
    "DataManager": 0,          # Gestor de Dados
    "VideoManager": 0,         # Gestor de Vídeos
    "GUI": 0,                  # Interface Gráfica
}

# 🔐 Tokens secretos por cliente (só o cliente e o servidor sabem)
AUTHORIZED_TOKENS = {
    "Assistant": "token_assistente_123",
    "Recorder": "token_recorder_123",
    "DiagnosticManager": "token_diag_123",
    "UserManager": "token_user_123",
    "ExercisesManager": "token_exercises_123",
    "DataManager": "token_data_123",
    "VideoManager": "token_video_123",
    "GUI": "token_gui_123",
}
VALID_TOKENS = {name: token for name, token in AUTHORIZED_TOKENS.items()}
# ============================================================
# 🔐 Função de autenticação (opcional)
# ============================================================
async def authenticate(websocket):
    """
    Autentica o cliente logo após a conexão.
    O cliente deve enviar um JSON no formato:
    {"auth": {"name": "Assistant", "token": "TOKEN_ASSISTANT_123"}}
    """
    try:
        message = await asyncio.wait_for(websocket.recv(), timeout=10)
        data = json.loads(message)

        if "auth" not in data:
            response = {"status": "error", "message": "Credenciais ausentes."}
            await websocket.send(json.dumps(response))
            raise ValueError("Cliente não enviou credenciais.")

        auth = data["auth"]
        name = auth.get("name")
        token = auth.get("token")

        if name not in VALID_TOKENS or VALID_TOKENS[name] != token:
            response = {"status": "error", "message": "Token inválido."}
            await websocket.send(json.dumps(response))
            raise ValueError(f"Autenticação falhou para {name}.")

        logging.info(f"✅ Cliente autenticado: {name}")
        return name

    except (asyncio.TimeoutError, json.JSONDecodeError, ValueError) as e:
        logging.warning(f"⚠️ Autenticação falhou: {e}")
        await websocket.close()
        return None


# ============================================================
# 👥 Handler principal de cada cliente
# ============================================================
async def handler(websocket):
    client_id = id(websocket)
    connected_clients[client_id] = websocket
    logging.info(f"🔌 Nova conexão ({client_id}).")

    try:

        # Autenticação antes de continuar
        client_name = await authenticate(websocket)
        if not client_name:
            return

        client_names[client_name] = client_id
        response = {"status": "authenticated", "client_id": client_id}
        await websocket.send(json.dumps(response))
        logging.info(f"🪪 {client_name} registrado com ID {client_id}")

        # Loop principal para receber mensagens
        async for message in websocket:
            logging.info(f"📩 [{client_name}] → {message}")
            await process_message(client_id, client_name, message)

    except websockets.exceptions.ConnectionClosed:
        logging.warning(f"🔌 {client_name if 'client_name' in locals() else 'Cliente'} desconectado inesperadamente.")

    finally:
        # Limpa registro
        connected_clients.pop(client_id, None)
        if 'client_name' in locals() and client_name in client_names:
            client_names[client_name] = 0
        logging.info(f"❌ Conexão encerrada: {client_name} ({client_id})")


# ============================================================
# 💬 Processamento de mensagens
# ============================================================
async def process_message(sender_id, sender_name, message):
    """Processa e encaminha mensagens entre os módulos."""
    try:
        data = json.loads(message)
        destination = data.get("destination")
        payload = data.get("data")

        if not payload:
            logging.warning(f"⚠️ Mensagem sem 'data' ignorada de {sender_name}")
            return

        if destination:
            await send_to_destination(destination, payload, sender_name)
        else:
            await broadcast(sender_id, payload, sender_name)

    except json.JSONDecodeError:
        logging.error(f"❌ JSON inválido recebido de {sender_name}: {message}")
    except Exception as e:
        logging.error(f"💥 Erro ao processar mensagem de {sender_name}: {e}")


# ============================================================
# 🎯 Envio direto para destino
# ============================================================
async def send_to_destination(destination, payload, sender_name):
    """Envia mensagem diretamente a um destino específico."""
    try:
        if destination in client_names and client_names[destination] in connected_clients:
            dest_id = client_names[destination]
            await connected_clients[dest_id].send(payload)
            logging.info(f"➡️ [{sender_name}] → [{destination}]")
        else:
            logging.warning(f"⚠️ Destino '{destination}' não está conectado.")
    except Exception as e:
        logging.error(f"💥 Erro ao enviar mensagem para {destination}: {e}")


# ============================================================
# 📢 Broadcast (envio global)
# ============================================================
async def broadcast(sender_id, message, sender_name):
    """Envia uma mensagem para todos os clientes, exceto o remetente."""
    # msg_json = json.dumps(message)
    tasks = []
    for cid, ws in connected_clients.items():
        if cid != sender_id:
            tasks.append(ws.send(message))
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
        logging.info(f"📡 Broadcast enviado por {sender_name} ({len(tasks)} destinatários)")


# ============================================================
# 🚀 Inicialização do servidor
# ============================================================
async def main():
    logging.info("🚀 Iniciando servidor WebSocket seguro...")

    server = await websockets.serve(
        handler,
        "localhost",
        8765,
        ping_interval=None  # Desativa timeout automático
    )

    logging.info("✅ Servidor rodando em ws://localhost:8765")
    await server.wait_closed()


# ============================================================
# 🏁 Ponto de entrada
# ============================================================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("🛑 Servidor encerrado manualmente.")
    except Exception as e:
        logging.critical(f"💥 Erro fatal: {e}")
