from datetime import date
from typing import List, Optional, Dict

mock_details = [
    {"user": "Gez", "user_type": "admin", "actions": 12, "date": "2025-07-10"},
    {"user": "Bob", "user_type": "client", "actions": 8, "date": "2025-07-14"},
    {"user": "Eve", "user_type": "admin", "actions": 15, "date": "2025-07-12"},
]

mock_summary = {
    "active_users": 125,
    "engagement_score": 89,
    "avg_session_time": "5m 12s"
}


def get_filtered_engagement_data(
    user_type: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
) -> Dict:
    filtered = []

    for entry in mock_details:
        if user_type and entry["user_type"] != user_type:
            continue
        if from_date and entry["date"] < str(from_date):
            continue
        if to_date and entry["date"] > str(to_date):
            continue
        filtered.append(entry)

    return {
        "summary": mock_summary,
        "details": filtered
    }
