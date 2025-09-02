from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from db.database import Base

# 설문 모델
class Survey(Base):
    __tablename__ = "surveys"

    id = Column(Integer, primary_key=True, index=True)
    family_type = Column(String(255), nullable=True)
    family_type_etc = Column(String(255), nullable=True)
    age_group = Column(String(255), nullable=True)
    job_type = Column(String(255), nullable=True)
    job_type_etc = Column(String(255), nullable=True)
    housing_type = Column(String(255), nullable=True)
    jeonse_budget = Column(String(255), nullable=True)
    maemae_budget = Column(String(255), nullable=True)
    monthly_cost = Column(String(255), nullable=True)
    work_school_location = Column(String(255), nullable=True)
    frequent_location = Column(String(255), nullable=True)
    other_location = Column(String(255), nullable=True)
    transport_method = Column(String(255), nullable=True)
    commute_time = Column(String(255), nullable=True)
    first_priority = Column(String(255), nullable=True)
    second_priority = Column(String(255), nullable=True)
    third_priority = Column(String(255), nullable=True)
    home_activity = Column(String(255), nullable=True)
    weekend_activity = Column(String(255), nullable=True)
    noise_sensitivity = Column(String(255), nullable=True)
    avoid_item = Column(String(255), nullable=True)
    avoid_item_etc = Column(String(255), nullable=True)
    want_item = Column(String(255), nullable=True)
    want_item_etc = Column(String(255), nullable=True)
    additional_comments = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}