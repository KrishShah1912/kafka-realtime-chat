from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

app = FastAPI()

# This class manages all connected users
class ConnectionManager:
    def __init__(self):
        # List of all active WebSocket connections
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        # Accept the connection first
        await websocket.accept()
        # Add to our list
        self.active_connections.append(websocket)
        print(f"New user connected! Total online: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        # Remove from our list when they leave
        self.active_connections.remove(websocket)
        print(f"User disconnected! Total online: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        # Send message to EVERYONE connected
        for connection in self.active_connections:
            await connection.send_text(message)

# Create one manager instance for the whole app
manager = ConnectionManager()

@app.get("/")
def root():
    return {
        "message": "Chat server is running!",
        "active_users": len(manager.active_connections)
    }

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    # Connect this user
    await manager.connect(websocket)

    # Tell everyone someone joined
    await manager.broadcast(f"🟢 {username} joined the chat!")

    try:
        # Keep listening for messages from this user
        while True:
            data = await websocket.receive_text()
            # Broadcast their message to everyone
            await manager.broadcast(f"{username}: {data}")
    except WebSocketDisconnect:
        # User closed their browser tab
        manager.disconnect(websocket)
        await manager.broadcast(f"🔴 {username} left the chat")
