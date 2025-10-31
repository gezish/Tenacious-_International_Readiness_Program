import asyncio
import json
import random
from datetime import datetime, timedelta
from aiokafka import AIOKafkaProducer
from faker import Faker

KAFKA_BOOTSTRAP = "localhost:9092"
KAFKA_TOPIC = "engagement-events"

fake = Faker()

async def produce():
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP)
    await producer.start()
    try:
        while True:
            # Generate fake engagement log
            event = {
                "user": fake.user_name(),
                "user_type": random.choice(["student", "teacher", "admin"]),
                "actions": random.randint(1, 20),
                "date": datetime.utcnow().isoformat()
            }

            value = json.dumps(event).encode("utf-8")
            await producer.send_and_wait(KAFKA_TOPIC, value=value)

            print("📤 Sent:", event)

            await asyncio.sleep(2)  # send every 2 seconds
    finally:
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(produce())