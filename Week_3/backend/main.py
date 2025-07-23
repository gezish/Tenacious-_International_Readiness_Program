from fastapi import FastAPI, UploadFile, File, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from io import StringIO
import csv
from datetime import datetime
from fastapi.responses import StreamingResponse
import io
from typing import Optional

from database import SessionLocal, engine
from models import EngagementLog, Base
import crud
import schemas
from fastapi.middleware.cors import CORSMiddleware

# DB setup
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# GET endpoint (already working)
@app.get("/engagement", response_model=schemas.EngagementResponse)
def read_engagement(
    user_type: str = Query(None),
    from_date: date = Query(None),
    to_date: date = Query(None),
    db: Session = Depends(get_db)
):
    return crud.get_engagement_data(db, user_type, from_date, to_date)

# ✅ NEW POST endpoint
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
                date=datetime.strptime(row["date"], "%Y-%m-%d").date()  # ✅ FIXED
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


@app.get("/engagement/export")
def export_engagement(
    user_type: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    logs = crud.get_engagement_data(db, user_type, from_date, to_date)["details"]

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["user", "user_type", "actions", "date"])
    for log in logs:
        writer.writerow([log.user, log.user_type, log.actions, log.date])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=engagement_export.csv"}
    )