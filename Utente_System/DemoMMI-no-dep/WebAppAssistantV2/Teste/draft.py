
import websocket
import threading
import time

# Endereço do servidor WebSocket
host = "localhost"
mmiCli_Out_add = f"ws://{host}:8005"

def im1_message_handler(ws, message):
    print(f"📩 Mensagem recebida do servidor: {message}")

def socket_open_handler(ws):
    print("✅ Conexão WebSocket aberta!")
    ws.send("Olá, servidor!")  # Enviar uma mensagem ao conectar

def on_error(ws, error):
    print(f"❌ Erro: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"🔌 Conexão fechada: {close_msg}, código {close_status_code}")

def run_websocket():
    websocket.enableTrace(True)  # Ativa logs de depuração
    ws = websocket.WebSocketApp(
        mmiCli_Out_add,
        on_message=im1_message_handler,
        on_open=socket_open_handler,
        on_error=on_error,
        on_close=on_close,
    )
    ws.run_forever()

# Rodar o cliente WebSocket em uma thread separada
ws_thread = threading.Thread(target=run_websocket, daemon=True)
ws_thread.start()

# Mantém o programa rodando
try:
    while True:
        time.sleep(1)  # Mantém o loop principal ativo sem bloquear
except KeyboardInterrupt:
    print("⏹️ Encerrando cliente WebSocket...")
