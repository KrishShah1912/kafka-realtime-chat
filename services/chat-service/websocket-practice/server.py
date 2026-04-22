import asyncio
import websockets

# This stores all currently connected users
connected_clients = set()

async def handler(websocket):
    # When someone connects, add them to our set
    connected_clients.add(websocket)
    print(f"New user connected! Total online: {len(connected_clients)}")

    try:
        # Keep listening for messages from this user
        async for message in websocket:
            print(f"Received: {message}")
            # Send that message to EVERYONE connected
            for client in connected_clients:
                await client.send(f"Someone said: {message}")
    finally:
        # When user disconnects, remove them
        connected_clients.remove(websocket)
        print(f"User disconnected! Total online: {len(connected_clients)}")

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("WebSocket server running on ws://localhost:8765")
        print("Waiting for connections...\n")
        await asyncio.Future()  # run forever

asyncio.run(main())