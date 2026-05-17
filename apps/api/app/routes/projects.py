from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.models import BrandAsset, Project
from app.schemas import BrandAssetRead, ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])
ALLOWED_EXTENSIONS = {".txt", ".md", ".csv"}


@router.post("", response_model=ProjectRead)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).order_by(Project.created_at.desc()).limit(50).all()


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return project


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(project_id: str, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    for key, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(project, key, " ".join(value.split()) if isinstance(value, str) else value)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db)):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    db.delete(project)
    db.commit()
    return {"ok": True}


@router.post("/{project_id}/brand-assets", response_model=BrandAssetRead)
async def upload_brand_asset(project_id: str, label: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    settings = get_settings()
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    filename = file.filename or "brand-kit.txt"
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Solo se permiten archivos .txt, .md o .csv")

    raw = await file.read(settings.max_brand_asset_bytes + 1)
    if len(raw) > settings.max_brand_asset_bytes:
        raise HTTPException(status_code=413, detail="El brand kit es demasiado grande. Usa un archivo más pequeño.")

    content = raw.decode("utf-8", errors="ignore").strip()
    if not content:
        raise HTTPException(status_code=400, detail="El archivo está vacío o no se pudo leer.")

    asset = BrandAsset(
        project_id=project_id,
        label=" ".join(label.split())[:80] or "brand-kit",
        content=content[: settings.max_brand_asset_bytes],
        metadata_json={"filename": filename, "content_type": file.content_type, "bytes": len(raw)},
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset
