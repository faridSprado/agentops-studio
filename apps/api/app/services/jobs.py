from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.models import Campaign, Project
from app.services.events import EventLog
from app.services.memory import project_memory
from app.services.workflow import AgentWorkflow


def run_campaign_job(campaign_id: str) -> None:
    db = SessionLocal()
    try:
        campaign = db.get(Campaign, campaign_id)
        if not campaign:
            return
        project = db.get(Project, campaign.project_id)
        if not project:
            campaign.status = "failed"
            campaign.error = "Project not found"
            db.commit()
            return
        log = EventLog(db, campaign.id)
        campaign.status = "running"
        campaign.error = ""
        db.commit()
        log.emit("system", "running", {"campaign_id": campaign.id})
        state = {
            "project": _project_payload(project),
            "brief": campaign.brief,
            "channels": campaign.channels or [],
            "language": campaign.language,
            "tone": campaign.tone,
            "human_review": campaign.human_review,
            "feedback": campaign.feedback or "",
            "memory": project_memory(db, project.id, campaign.brief),
            "revision_count": 0,
        }
        result = AgentWorkflow(settings=get_settings(), emit=log.emit).run(state)
        campaign.output = result.get("final")
        campaign.score = int(result.get("score") or 0)
        campaign.status = result.get("status") or "completed"
        db.commit()
        log.emit("system", campaign.status, {"score": campaign.score})
    except Exception as exc:
        _fail(db, campaign_id, exc)
    finally:
        db.close()


def _project_payload(project: Project) -> dict:
    return {
        "id": project.id,
        "name": project.name,
        "brand_voice": project.brand_voice,
        "audience": project.audience,
        "constraints": project.constraints,
    }


def _fail(db: Session, campaign_id: str, exc: Exception) -> None:
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        return
    campaign.status = "failed"
    campaign.error = str(exc)
    db.commit()
    EventLog(db, campaign_id).emit("system", "failed", {"error": str(exc)})
