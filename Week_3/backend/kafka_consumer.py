# kafka_consumer.py
import asyncio
import json
from aiokafka import AIOKafkaConsumer
from sqlalchemy.orm import Session
from database import SessionLocal
from models import EngagementLog
from datetime import datetime

KAFKA_BOOTSTRAP = "localhost:9092"
KAFKA_TOPIC = "engagement-events"

async def consume():
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id="engagement-group",
        auto_offset_reset="earliest"   # read from beginning if no offset
    )

    await consumer.start()
    try:
        async for msg in consumer:
            try:
                data = json.loads(msg.value.decode("utf-8"))

                # Ensure date is parsed correctly
                date_str = data.get("date")
                try:
                    parsed_date = datetime.fromisoformat(date_str.replace("Z", "")) if date_str else datetime.utcnow()
                except Exception:
                    parsed_date = datetime.utcnow()

                log = EngagementLog(
                    user=data.get("user"),
                    user_type=data.get("user_type"),
                    actions=int(data.get("actions", 0)),
                    date=parsed_date
                )

                db: Session = SessionLocal()
                db.add(log)
                db.commit()
                db.refresh(log)
                db.close()

                print(f"✅ Inserted into DB: {log.user}, {log.user_type}, {log.actions}, {log.date}")

            except Exception as e:
                print("❌ Error processing message:", e)

    finally:
        await consumer.stop()
