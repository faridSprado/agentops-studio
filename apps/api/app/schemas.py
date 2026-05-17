from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

ALLOWED_CHANNELS = {"instagram", "tiktok", "landing", "email", "youtube", "linkedin"}


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    brand_voice: str = Field(default="", max_length=260)
    audience: str = Field(default="", max_length=260)
    constraints: str = Field(default="", max_length=420)

    @field_validator("name", "brand_voice", "audience", "constraints")
    @classmethod
    def clean_text(cls, value: str) -> str:
        return " ".join((value or "").split())


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    brand_voice: str | None = Field(default=None, max_length=260)
    audience: str | None = Field(default=None, max_length=260)
    constraints: str | None = Field(default=None, max_length=420)


class ProjectRead(BaseModel):
    id: str
    name: str
    brand_voice: str
    audience: str
    constraints: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BrandAssetRead(BaseModel):
    id: str
    project_id: str
    label: str
    content: str
    metadata_json: dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CampaignCreate(BaseModel):
    brief: str = Field(min_length=10, max_length=2200)
    channels: list[str] = Field(default_factory=lambda: ["instagram", "tiktok", "landing"], min_length=1, max_length=6)
    language: str = Field(default="es", max_length=10)
    tone: str = Field(default="profesional", max_length=180)
    human_review: bool = False

    @field_validator("brief", "tone", "language")
    @classmethod
    def clean_text(cls, value: str) -> str:
        return " ".join((value or "").split())

    @field_validator("channels")
    @classmethod
    def validate_channels(cls, value: list[str]) -> list[str]:
        channels = []
        for channel in value:
            clean = str(channel).lower().strip()
            if clean in ALLOWED_CHANNELS and clean not in channels:
                channels.append(clean)
        if not channels:
            raise ValueError("Selecciona al menos un canal válido.")
        return channels[:6]


class CampaignRename(BaseModel):
    title: str = Field(min_length=2, max_length=160)

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        return " ".join((value or "").split())


class FeedbackCreate(BaseModel):
    feedback: str = Field(min_length=3, max_length=900)

    @field_validator("feedback")
    @classmethod
    def clean_feedback(cls, value: str) -> str:
        return " ".join((value or "").split())


class CampaignRead(BaseModel):
    id: str
    project_id: str
    brief: str
    channels: list[str]
    language: str
    tone: str
    human_review: bool
    feedback: str
    status: str
    output: dict[str, Any] | None
    score: int | None
    error: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentEventRead(BaseModel):
    id: str
    campaign_id: str
    sequence: int
    agent: str
    status: str
    payload: dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentOutput(BaseModel):
    title: str
    summary: str
    items: list[str] = Field(default_factory=list)
    data: dict[str, Any] = Field(default_factory=dict)
