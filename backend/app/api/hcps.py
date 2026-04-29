from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models import HCP
from app.schemas import HCPCreate, HCPResponse
from app.database import get_db

router = APIRouter()


@router.get("/", response_model=List[HCPResponse])
def list_hcps(search: str = None, db: Session = Depends(get_db)):
    query = db.query(HCP)
    if search:
        query = query.filter(HCP.name.ilike(f"%{search}%"))
    return query.limit(50).all()


@router.post("/", response_model=HCPResponse)
def create_hcp(data: HCPCreate, db: Session = Depends(get_db)):
    hcp = HCP(**data.model_dump())
    db.add(hcp)
    db.commit()
    db.refresh(hcp)
    return hcp


@router.get("/{hcp_id}", response_model=HCPResponse)
def get_hcp(hcp_id: int, db: Session = Depends(get_db)):
    hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")
    return hcp
