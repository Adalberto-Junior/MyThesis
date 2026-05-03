
"""""
import asyncio
import websockets

async def client():
    async with websockets.connect("ws://localhost:8005") as websocket:
        # Recebe o próprio ID
        greeting = await websocket.recv()
        print(greeting)
        my_id = greeting.split()[-1]
        print(f"Meu ID é {my_id}")

        # Loop para enviar mensagens
        while True:
            message = input("Digite sua mensagem: ")
            await websocket.send(message)
            response = await websocket.recv()
            print(f"Recebido: {response}")

asyncio.get_event_loop().run_until_complete(client())
"""""

import asyncio
import websockets

async def communicate_with_server(uri, server_name):
    async with websockets.connect(uri) as websocket:
        print(f"Conectado ao {server_name} em {uri}")

        # Cria uma tarefa para receber mensagens do servidor
        receive_task = asyncio.create_task(receive_messages(websocket, server_name))

        # Loop para enviar mensagens ao servidor
        while True:
            message = await ainput(f"[{server_name}] Digite sua mensagem (ou 'sair' para desconectar): ")
            if message.lower() == 'sair':
                print(f"Desconectando de {server_name}...")
                break
            await websocket.send(message)

        # Cancela a tarefa de recebimento ao sair
        receive_task.cancel()
        await websocket.close()
        print(f"Conexão com {server_name} encerrada.")

async def receive_messages(websocket, server_name):
    try:
        async for message in websocket:
            print(f"\n[{server_name}] Recebido: {message}")
    except websockets.exceptions.ConnectionClosed:
        print(f"Conexão com {server_name} foi fechada pelo servidor.")

async def ainput(prompt: str = '') -> str:
    return await asyncio.get_event_loop().run_in_executor(None, lambda: input(prompt))

async def main():
    # Lista de servidores
    servers = [
        ("ws://localhost:8765", "Servidor 1"),
        ("ws://localhost:8766", "Servidor 2"),
    ]

    # Cria tarefas para cada servidor
    tasks = [communicate_with_server(uri, name) for uri, name in servers]

    # Executa todas as tarefas simultaneamente
    await asyncio.gather(*tasks)

# Inicia o programa
if __name__ == '__main__':
    asyncio.run(main())
