from fastapi import FastAPI
from kafka import KafkaProducer
import json
import time

app = FastAPI()

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

@app.get("/")
def root():
    return {"message": "Mini chat pipeline is running!"}

@app.post("/send")
def send_message(user: str, text: str):
    message = {
        "user": user,
        "text": text,
        "time": time.time()
    }
    producer.send('chat', message)
    return {"status": "message sent to Kafka!", "message": message}