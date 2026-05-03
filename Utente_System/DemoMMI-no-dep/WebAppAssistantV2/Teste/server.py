
import asyncio
import websockets

# Armazena as conexões dos clientes com seus IDs
connected_clients = {}

async def handler(websocket):
    # Atribuímos um ID único ao cliente (por exemplo, usando id())
    client_id = id(websocket)
    connected_clients[client_id] = websocket
    print(f"Cliente {client_id} conectado.")

    try:
        # Enviamos o ID para o cliente recém-conectado
        await websocket.send(f"Seu ID é {client_id}")

        async for message in websocket:
            print(f"Mensagem recebida de {client_id}: {message}")

            # Processa a mensagem recebida
            await process_message(client_id, message)
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Remove o cliente da lista quando ele se desconecta
        del connected_clients[client_id]
        print(f"Cliente {client_id} desconectado.")

async def process_message(sender_id, message):
    if ":" in message:
        # Formato esperado: "destinatario_id:mensagem"
        target_id_str, msg = message.split(":", 1)
        target_id = int(target_id_str)
        if target_id in connected_clients:
            await connected_clients[target_id].send(f"{sender_id} diz: {msg}")
            print(f"Enviou para {target_id}: {msg}")
        else:
            await connected_clients[sender_id].send("Cliente alvo não está conectado.")
    else:
        # Se não especificar destinatário, envia para todos
        await broadcast(sender_id, message)

async def broadcast(sender_id, message):
    for client_id, websocket in connected_clients.items():
        if client_id != sender_id:
            await websocket.send(f"{sender_id} para todos: {message}")

#start_server = websockets.serve(handler, "localhost", 8005)

#print("Servidor iniciado na porta 8005. Aguardando conexões...")
#asyncio.get_event_loop().run_until_complete(start_server)
#asyncio.get_event_loop().run_forever()

async def main():
    print("🚀 Iniciando servidor WebSocket...")

    # Criando o servidor WebSocket de forma explícita
    server = await websockets.serve(handler, "localhost", 8765, ping_interval=None)

    print("✅ Servidor WebSocket rodando em ws://localhost:8765")

    # Mantém o servidor ativo
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())  # Garante que o loop de eventos está correto
    except RuntimeError as e:
        print(f"⚠️ Erro de execução do asyncio: {e}")


"""""
import asyncio
import websockets

async def handler(websocket):
    path = "Desconhecido"
    print(f"✅ Cliente conectado: {websocket.remote_address}")
    

    try:
        while True:
            command = input("Digite 'gravar' para iniciar a gravação ou 'terminar' para parar a gravação: ")
            await websocket.send(command)
            response = await websocket.recv()
            print(f"Feedback do cliente: {response}")

    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ Conexão fechada: {e}")
    except Exception as e:
        print(f"⚠️ Erro inesperado: {e}")
    finally:
        print("🔌 Cliente desconectado.")

async def main():
    print("🚀 Iniciando servidor WebSocket...")

    # Criando o servidor WebSocket de forma explícita
    server = await websockets.serve(handler, "localhost", 8005, ping_interval=None)

    print("✅ Servidor WebSocket rodando em ws://localhost:8005")

    # Mantém o servidor ativo
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())  # Garante que o loop de eventos está correto
    except RuntimeError as e:
        print(f"⚠️ Erro de execução do asyncio: {e}")
"""""
