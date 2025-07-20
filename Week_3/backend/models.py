from sqlalchemy import Column, Integer, String, Date
from database import Base

class EngagementLog(Base):
    __tablename__ = "engagement_logs"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, nullable=False)
    user_type = Column(String, nullable=False)
    actions = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
