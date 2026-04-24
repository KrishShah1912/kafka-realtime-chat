from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import redis.asyncio as aioredis
import json

app = FastAPI()

# Connect to Redis
redis_client = aioredis.from_url("redis://localhost:6379")

# Still keep track of who is connected to THIS server
connected_clients = set()

# This function runs in the background forever
# It listens to Redis and delivers messages to connected users
async def redis_listener():
    pubsub = redis_client.pubsub()
    
    # Subscribe to the "chat" channel on Redis
    await pubsub.subscribe("chat")
    print("Listening to Redis chat channel...")

    # Keep listening forever
    async for message in pubsub.listen():
        # Redis sends a subscription confirmation first, ignore it
        if message["type"] == "message":
            text = message["data"].decode()
            print(f"Received from Redis: {text}")
            
            # Deliver to all users connected to THIS server
            for client in connected_clients.copy():
                try:
                    await client.send_text(text)
                except:
                    # If sending fails, remove that client
                    connected_clients.discard(client)

# Start the Redis listener when server starts
@app.on_event("startup")
async def startup():
    asyncio.create_task(redis_listener())
    print("Redis listener started!")

@app.get("/")
def root():
    return {
        "message": "Redis pub/sub chat running!",
        "connected_users": len(connected_clients)
    }

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()
    connected_clients.add(websocket)
    print(f"{username} connected! Total: {len(connected_clients)}")

    # Announce to everyone via Redis
    join_message = json.dumps({
        "user": "System",
        "text": f"{username} joined the chat!"
    })
    await redis_client.publish("chat", join_message)

    try:
        while True:
            data = await websocket.receive_text()
            
            # Instead of broadcasting directly to clients
            # we publish to Redis first
            message = json.dumps({
                "user": username,
                "text": data
            })
            await redis_client.publish("chat", message)
            print(f"Published to Redis: {message}")

    except WebSocketDisconnect:
        connected_clients.discard(websocket)
        print(f"{username} disconnected!")
        
        # Announce leaving via Redis
        leave_message = json.dumps({
            "user": "System",
            "text": f"{username} left the chat"
        })
        await redis_client.publish("chat", leave_message)
