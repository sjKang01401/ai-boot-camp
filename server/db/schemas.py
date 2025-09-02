from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SurveyBase(BaseModel):
    family_type: Optional[str] = None
    family_type_etc: Optional[str] = None
    age_group: Optional[str] = None
    job_type: Optional[str] = None
    job_type_etc: Optional[str] = None
    housing_type: Optional[str] = None
    jeonse_budget: Optional[str] = None
    maemae_budget: Optional[str] = None
    monthly_cost: Optional[str] = None
    work_school_location: Optional[str] = None
    frequent_location: Optional[str] = None
    other_location: Optional[str] = None
    transport_method: Optional[str] = None
    commute_time: Optional[str] = None
    first_priority: Optional[str] = None
    second_priority: Optional[str] = None
    third_priority: Optional[str] = None
    home_activity: Optional[str] = None
    weekend_activity: Optional[str] = None
    noise_sensitivity: Optional[str] = None
    avoid_item: Optional[str] = None
    avoid_item_etc: Optional[str] = None
    want_item: Optional[str] = None
    want_item_etc: Optional[str] = None
    additional_comments: Optional[str] = None


class SurveyCreate(SurveyBase):
    pass


class SurveySchema(SurveyBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }