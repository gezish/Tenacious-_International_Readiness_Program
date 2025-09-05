from fastapi import FastAPI, UploadFile, File, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, datetime
from io import StringIO
import csv
from fastapi.responses import StreamingResponse
import io
from typing import Optional

from database import SessionLocal, engine
from models import EngagementLog, Base
import crud
import schemas
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from kafka_consumer import consume

# DB setup
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Allow frontend React app to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to ["http://localhost:3000"] for stricter security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    loop = asyncio.get_event_loop()
    loop.create_task(consume())  # run Kafka consumer in background


@app.get("/")
def root():
    return {"msg": "🚀 FastAPI backend with Kafka running"}


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ FIXED GET endpoint (always returns summary + details)
@app.get("/engagement")
def read_engagement(
    user_type: str = Query(None),
    from_date: date = Query(None),
    to_date: date = Query(None),
    db: Session = Depends(get_db),
):
    try:
        result = crud.get_engagement_data(db, user_type, from_date, to_date)

        # Guarantee correct response shape
        summary = result.get("summary", {
            "active_users": 0,
            "engagement_score": 0,
            "avg_session_time": 0
        })

        details = result.get("details", [])
        if not isinstance(details, list):
            details = []

        # Ensure all dates are JSON serializable
        safe_details = []
        for log in details:
            safe_details.append({
                "user": getattr(log, "user", None) or log.get("user"),
                "user_type": getattr(log, "user_type", None) or log.get("user_type"),
                "actions": getattr(log, "actions", None) or log.get("actions"),
                "date": (
                    log.date.isoformat() if hasattr(log, "date") and isinstance(log.date, (date, datetime))
                    else str(log.get("date")) if isinstance(log, dict) and "date" in log
                    else None
                )
            })

        return {"summary": summary, "details": safe_details}

    except Exception as e:
        print("❌ Error in /engagement:", e)
        return {
            "summary": {"active_users": 0, "engagement_score": 0, "avg_session_time": 0},
            "details": []
        }


# ✅ CSV Import
@app.post("/engagement/import")
def import_engagement(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        content = file.file.read().decode("utf-8")
        csv_reader = csv.DictReader(StringIO(content))

        required_fields = {"user", "user_type", "actions", "date"}
        if not required_fields.issubset(csv_reader.fieldnames):
            return {"error": f"CSV must contain columns: {', '.join(required_fields)}"}

        imported = 0
        for row in csv_reader:
            try:
                log = EngagementLog(
                    user=row["user"],
                    user_type=row["user_type"],
                    actions=int(row["actions"]),
                    date=datetime.strptime(row["date"], "%Y-%m-%d").date()
                )
                db.add(log)
                imported += 1
            except Exception as row_error:
                print("Row skipped due to error:", row_error)
                continue

        db.commit()
        return {"message": f"Successfully imported {imported} rows."}

    except Exception as e:
        print("Full error:", e)
        return {"error": "Internal Server Error. See logs."}


# ✅ CSV Export
@app.get("/engagement/export")
def export_engagement(
    user_type: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    logs = crud.get_engagement_data(db, user_type, from_date, to_date).get("details", [])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["user", "user_type", "actions", "date"])

    for log in logs:
        writer.writerow([
            getattr(log, "user", None) or log.get("user"),
            getattr(log, "user_type", None) or log.get("user_type"),
            getattr(log, "actions", None) or log.get("actions"),
            getattr(log, "date", None) if hasattr(log, "date") else log.get("date")
        ])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=engagement_export.csv"}
    )
