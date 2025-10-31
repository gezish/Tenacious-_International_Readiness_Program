from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from datetime import datetime

class EngagementLog(Base):
    __tablename__ = "engagement_logs"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, index=True)
    user_type = Column(String, index=False)
    actions = Column(Integer, default=0)
    date = Column(DateTime, default=datetime.utcnow)
