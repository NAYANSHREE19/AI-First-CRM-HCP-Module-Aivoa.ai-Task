from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class HCP(Base):
    __tablename__ = "hcps"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    specialty = Column(String(200))
    email = Column(String(200))
    phone = Column(String(50))
    institution = Column(String(300))
    created_at = Column(DateTime, default=datetime.utcnow)
    interactions = relationship("Interaction", back_populates="hcp")


class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id"), nullable=True)
    hcp_name = Column(String(200))
    interaction_type = Column(String(50), default="meeting")
    date = Column(DateTime, default=datetime.utcnow)
    attendees = Column(Text)
    topics_discussed = Column(Text)
    materials_shared = Column(Text)
    samples_distributed = Column(Text)
    sentiment = Column(String(20), default="neutral")
    outcomes = Column(Text)
    follow_up_actions = Column(Text)
    raw_summary = Column(Text)
    extra_data = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    hcp = relationship("HCP", back_populates="interactions")
