# 📊 Engagement Module – Backend API

## 👤 Author
Gezahegne Wondachew  
Week 3 – International Readiness Program

## 📌 Project Overview
This backend API provides filterable engagement analytics for internal dashboards. It includes CSV data ingestion and export functionality, and summary statistics useful for visualization.

---

## 🚀 Features

### ✅ `/engagement` (GET)
- Returns filtered engagement logs
- Filters:
  - `user_type`
  - `from_date`, `to_date`
- Includes:
  - `summary`: aggregate metrics
  - `details`: per-user logs

### ✅ `/engagement/import` (POST)
- Accepts `.csv` file
- Parses and stores data into SQLite database

### ✅ `/engagement/export` (GET)
- Exports current filtered results as a downloadable `.csv` file

---

## 🧠 Engagement Log Fields
- `user`, `user_type`, `actions`, `date`

---

## 🔄 Summary Metrics (Auto Calculated)
- `active_users`
- `engagement_score` (placeholder logic)
- `avg_session_time` (based on action weight)

---

## 🧱 Tech Stack
- FastAPI
- SQLAlchemy + SQLite
- CSV File Handling
- Pydantic for validation
- CORS enabled (for frontend integration)

---

## 🛠 Setup Instructions

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
