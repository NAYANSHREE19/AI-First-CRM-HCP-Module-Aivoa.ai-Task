from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class HCPBase(BaseModel):
    name: str
    specialty: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    institution: Optional[str] = None


class HCPCreate(HCPBase):
    pass


class HCPResponse(HCPBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class InteractionBase(BaseModel):
    hcp_id: Optional[int] = None
    hcp_name: Optional[str] = None
    interaction_type: Optional[str] = "meeting"
    date: Optional[datetime] = None
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    materials_shared: Optional[str] = None
    samples_distributed: Optional[str] = None
    sentiment: Optional[str] = "neutral"
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None
    raw_summary: Optional[str] = None


class InteractionCreate(InteractionBase):
    pass


class InteractionUpdate(InteractionBase):
    pass


class InteractionResponse(InteractionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    message: str
    conversation_history: Optional[List[dict]] = []
    current_form_data: Optional[dict] = {}


class ChatResponse(BaseModel):
    reply: str
    form_updates: Optional[dict] = None
    action: Optional[str] = None
    interaction_id: Optional[int] = None
