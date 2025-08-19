from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date, time, datetime

class InteractionBase(BaseModel):
    hcp_name: str = Field(..., max_length=255)
    interaction_type: str
    date: date
    time: time
    attendees: Optional[List[str]] = None
    topics_discussed: str
    voice_note_summary: Optional[str] = None
    materials_shared: Optional[List[str]] = None
    samples_distributed: Optional[List[str]] = None
    sentiment: str
    outcomes: Optional[str] = None
    follow_up_actions: Optional[List[str]] = None
    ai_suggested_followups: Optional[List[str]] = None

    # --- NEW VALIDATORS ADDED BELOW ---
    @validator('interaction_type')
    def validate_interaction_type(cls, v):
        allowed_values = ["Meeting", "Call", "Virtual"]
        if v not in allowed_values:
            raise ValueError(f"'{v}' is not a valid interaction type. Must be one of {allowed_values}")
        return v

    @validator('sentiment')
    def validate_sentiment(cls, v):
        allowed_values = ["Positive", "Neutral", "Negative"]
        if v not in allowed_values:
            raise ValueError(f"'{v}' is not a valid sentiment. Must be one of {allowed_values}")
        return v


class InteractionCreate(InteractionBase):
    pass

class InteractionOut(InteractionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class PaginatedHistoryResponse(BaseModel):
    data: List[InteractionOut]
    pagination: dict