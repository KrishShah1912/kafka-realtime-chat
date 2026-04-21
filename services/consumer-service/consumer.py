from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'chat',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("Consumer running! Waiting for messages...\n")

for message in consumer:
    msg = message.value
    print(f"New message from [{msg['user']}]: {msg['text']}")
