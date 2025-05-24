from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class FeedbackBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    username: str
    email: EmailStr
    category: str
    message: str


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackResponse(FeedbackBase):
    id: int
    status: str
    created_time: datetime


class FeedbackList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    feedbacks: List[FeedbackResponse]
    total: int 