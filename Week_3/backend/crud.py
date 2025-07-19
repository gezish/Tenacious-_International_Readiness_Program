from sqlalchemy.orm import Session
from models import EngagementLog
from datetime import date
from typing import Optional

def get_engagement_data(
    db: Session,
    user_type: Optional[str],
    from_date: Optional[date],
    to_date: Optional[date]
):
    query = db.query(EngagementLog)

    if user_type:
        query = query.filter(EngagementLog.user_type == user_type)
    if from_date:
        query = query.filter(EngagementLog.date >= from_date)
    if to_date:
        query = query.filter(EngagementLog.date <= to_date)

    records = query.all()

    # ✅ Dynamic summary calculation
    total_actions = sum(r.actions for r in records)
    num_users = len(records)
    engagement_score = int(min(100, total_actions))  # Placeholder logic

    avg_time_minutes = total_actions * 0.5  # fake formula: 0.5 min per action
    avg_time = f"{int(avg_time_minutes)}m {int((avg_time_minutes % 1) * 60)}s"

    summary = {
        "active_users": num_users,
        "engagement_score": engagement_score,
        "avg_session_time": avg_time
    }

    return {
        "summary": summary,
        "details": records
    }