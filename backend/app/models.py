from sqlalchemy import (Column, Integer, String, DateTime, Text, Enum, JSON, Date, Time)
from .database import Base
import enum
from datetime import datetime

class InteractionTypeEnum(str, enum.Enum):
    Meeting = "Meeting"
    Call = "Call"
    Virtual = "Virtual"

class SentimentEnum(str, enum.Enum):
    Positive = "Positive"
    Neutral = "Neutral"
    Negative = "Negative"

class HCPInteraction(Base):
    __tablename__ = "hcp_interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String(255), nullable=False)
    
    # --- FIX APPLIED HERE ---
    # The 'values_callable' tells SQLAlchemy to use the .value of the enum
    interaction_type = Column(
        Enum(InteractionTypeEnum, values_callable=lambda x: [e.value for e in x]), 
        nullable=False
    )
    
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    attendees = Column(JSON, nullable=True)
    topics_discussed = Column(Text, nullable=False)
    voice_note_summary = Column(Text, nullable=True)
    materials_shared = Column(JSON, nullable=True)
    samples_distributed = Column(JSON, nullable=True)
    
    # --- AND FIX APPLIED HERE ---
    sentiment = Column(
        Enum(SentimentEnum, values_callable=lambda x: [e.value for e in x]), 
        nullable=False
    )
    
    outcomes = Column(Text, nullable=True)
    follow_up_actions = Column(JSON, nullable=True)
    ai_suggested_followups = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)