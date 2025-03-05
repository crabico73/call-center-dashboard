from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class CallBase(BaseModel):
    company_id: int
    contact_id: int
    agent_id: str
    scheduled_at: Optional[datetime] = None

class CallCreate(CallBase):
    pass

class Call(CallBase):
    id: int
    call_sid: Optional[str] = None
    status: str
    duration: Optional[int] = None
    recording_url: Optional[str] = None
    transcript: Optional[str] = None
    sentiment_score: Optional[float] = None
    conversation_data: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True 