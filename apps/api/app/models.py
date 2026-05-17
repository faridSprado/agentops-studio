from uuid import uuid4

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.db import Base
from app.core.time import utc_now


def make_id() -> str:
    return str(uuid4())


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=make_id)
    name = Column(String(220), nullable=False)
    brand_voice = Column(Text, default="")
    audience = Column(Text, default="")
    constraints = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    campaigns = relationship("Campaign", back_populates="project", cascade="all, delete-orphan")
    brand_assets = relationship("BrandAsset", back_populates="project", cascade="all, delete-orphan")


class BrandAsset(Base):
    __tablename__ = "brand_assets"

    id = Column(String, primary_key=True, default=make_id)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    label = Column(String(220), nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    project = relationship("Project", back_populates="brand_assets")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String, primary_key=True, default=make_id)
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    brief = Column(Text, nullable=False)
    channels = Column(JSON, default=list)
    language = Column(String(20), default="es")
    tone = Column(String(120), default="profesional")
    human_review = Column(Boolean, default=False)
    feedback = Column(Text, default="")
    status = Column(String(40), default="queued", index=True)
    output = Column(JSON, nullable=True)
    score = Column(Integer, nullable=True)
    error = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    project = relationship("Project", back_populates="campaigns")
    events = relationship("AgentEvent", back_populates="campaign", cascade="all, delete-orphan")


class AgentEvent(Base):
    __tablename__ = "agent_events"

    id = Column(String, primary_key=True, default=make_id)
    campaign_id = Column(String, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    sequence = Column(Integer, nullable=False)
    agent = Column(String(80), nullable=False)
    status = Column(String(40), nullable=False)
    payload = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    campaign = relationship("Campaign", back_populates="events")
