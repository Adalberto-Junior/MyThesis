import asyncio
import websockets

async def echo(websocket):
    try:
        async for message in websocket:
            print(f"Mensagem recebida: {message}")
            response = f"ECHO: {message}"
            await websocket.send(response)
    except websockets.exceptions.ConnectionClosed:
        print("Cliente desconectado.")

#start_server = websockets.serve(echo, "localhost", 8766)

#asyncio.get_event_loop().run_until_complete(start_server)
#print("Servidor WebSocket rodando na porta 8766.")
#asyncio.get_event_loop().run_forever()

async def main():
    print("🚀 Iniciando servidor WebSocket...")

    # Criando o servidor WebSocket de forma explícita
    server = await websockets.serve(echo, "localhost", 8766)

    print("✅ Servidor WebSocket rodando em ws://localhost:8766")

    # Mantém o servidor ativo
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())  # Garante que o loop de eventos está correto
    except RuntimeError as e:
        print(f"⚠️ Erro de execução do asyncio: {e}")
