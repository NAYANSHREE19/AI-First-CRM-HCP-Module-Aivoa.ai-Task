from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import ChatMessage, ChatResponse
from app.agents.hcp_agent import run_agent
from app.database import get_db

router = APIRouter()


@router.post("/", response_model=ChatResponse)
def chat(payload: ChatMessage, db: Session = Depends(get_db)):
    result = run_agent(
        message=payload.message,
        conversation_history=payload.conversation_history or [],
        db=db,
    )
    return ChatResponse(
        reply=result["reply"],
        form_updates=result.get("form_updates"),
        action=result.get("action"),
        interaction_id=result.get("interaction_id"),
    )
