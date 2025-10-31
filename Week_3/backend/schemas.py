from pydantic import BaseModel
from datetime import datetime

class EngagementEntry(BaseModel):
    user: str
    user_type: str
    actions: int
    date: datetime

    class Config:
        orm_mode = True

class EngagementSummary(BaseModel):
    active_users: int
    engagement_score: int
    avg_session_time: str

class EngagementResponse(BaseModel):
    summary: EngagementSummary
    details: list[EngagementEntry]
