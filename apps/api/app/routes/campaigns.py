from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import AgentEvent, Campaign, Project
from app.schemas import AgentEventRead, CampaignCreate, CampaignRead, CampaignRename, FeedbackCreate
from app.services.events import EventLog
from app.services.exporter import campaign_json, campaign_markdown, campaign_pdf, campaign_zip
from app.services.jobs import run_campaign_job

router = APIRouter(tags=["campaigns"])


@router.post("/projects/{project_id}/campaigns", response_model=CampaignRead, status_code=202)
def create_campaign(project_id: str, payload: CampaignCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    campaign = Campaign(project_id=project_id, **payload.model_dump(), status="queued")
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    EventLog(db, campaign.id).emit("system", "queued", {})
    background_tasks.add_task(run_campaign_job, campaign.id)
    return campaign


@router.get("/campaigns/{campaign_id}", response_model=CampaignRead)
def get_campaign(campaign_id: str, db: Session = Depends(get_db)):
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.patch("/campaigns/{campaign_id}/title", response_model=CampaignRead)
def rename_campaign(campaign_id: str, payload: CampaignRename, db: Session = Depends(get_db)):
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    title = " ".join(payload.title.split())[:160]
    output = dict(campaign.output or {})
    output["title"] = title
    campaign.output = output if output else None
    if campaign.project:
        campaign.project.name = title
    db.commit()
    db.refresh(campaign)
    return campaign


@router.delete("/campaigns/{campaign_id}", status_code=204)
def delete_campaign(campaign_id: str, db: Session = Depends(get_db)):
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    db.delete(campaign)
    db.commit()
    return Response(status_code=204)


@router.get("/campaigns/{campaign_id}/events", response_model=list[AgentEventRead])
def get_campaign_events(campaign_id: str, db: Session = Depends(get_db)):
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return db.query(AgentEvent).filter(AgentEvent.campaign_id == campaign_id).order_by(AgentEvent.sequence.asc()).all()


@router.post("/campaigns/{campaign_id}/run", response_model=CampaignRead, status_code=202)
def rerun_campaign(campaign_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    campaign.status = "queued"
    campaign.output = None
    campaign.score = None
    campaign.error = ""
    db.commit()
    db.refresh(campaign)
    EventLog(db, campaign.id).emit("system", "queued", {"rerun": True})
    background_tasks.add_task(run_campaign_job, campaign.id)
    return campaign


@router.post("/campaigns/{campaign_id}/feedback", response_model=CampaignRead, status_code=202)
def add_feedback(campaign_id: str, payload: FeedbackCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    campaign.feedback = payload.feedback
    campaign.status = "queued"
    campaign.output = None
    campaign.error = ""
    db.commit()
    db.refresh(campaign)
    EventLog(db, campaign.id).emit("human", "feedback", {"feedback": payload.feedback})
    background_tasks.add_task(run_campaign_job, campaign.id)
    return campaign


@router.post("/campaigns/{campaign_id}/approve", response_model=CampaignRead)
def approve_campaign(campaign_id: str, db: Session = Depends(get_db)):
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    campaign.status = "completed"
    db.commit()
    db.refresh(campaign)
    EventLog(db, campaign.id).emit("human", "approved", {})
    return campaign


@router.get("/campaigns/{campaign_id}/export/{fmt}")
def export_campaign(campaign_id: str, fmt: str, db: Session = Depends(get_db)):
    campaign = db.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if not campaign.output:
        raise HTTPException(status_code=409, detail="Campaign has no output yet")
    name = campaign.output.get("title", "campaign").lower().replace(" ", "-")[:40]
    if fmt == "json":
        return Response(campaign_json(campaign.output), media_type="application/json", headers={"Content-Disposition": f"attachment; filename={name}.json"})
    if fmt == "markdown":
        return Response(campaign_markdown(campaign.output), media_type="text/markdown", headers={"Content-Disposition": f"attachment; filename={name}.md"})
    if fmt == "pdf":
        return Response(campaign_pdf(campaign.output), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={name}.pdf"})
    if fmt == "zip":
        return Response(campaign_zip(campaign.output), media_type="application/zip", headers={"Content-Disposition": f"attachment; filename={name}.zip"})
    raise HTTPException(status_code=400, detail="Unsupported format")
