from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models import Interaction
from app.schemas import InteractionCreate, InteractionUpdate, InteractionResponse
from app.database import get_db
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[InteractionResponse])
def list_interactions(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Interaction).order_by(Interaction.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{interaction_id}", response_model=InteractionResponse)
def get_interaction(interaction_id: int, db: Session = Depends(get_db)):
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction

@router.post("/", response_model=InteractionResponse)
def create_interaction(data: InteractionCreate, db: Session = Depends(get_db)):
    interaction = Interaction(**data.model_dump())
    if not interaction.date:
        interaction.date = datetime.utcnow()
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction

@router.put("/{interaction_id}", response_model=InteractionResponse)
def update_interaction(interaction_id: int, data: InteractionUpdate, db: Session = Depends(get_db)):
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(interaction, k, v)
    interaction.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(interaction)
    return interaction

@router.delete("/{interaction_id}")
def delete_interaction(interaction_id: int, db: Session = Depends(get_db)):
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    db.delete(interaction)
    db.commit()
    return {"message": "Deleted successfully"}
