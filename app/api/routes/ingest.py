from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import User
from app.api.deps import get_current_user, require_role_dep
from app.api.schemas.ingest import IngestPreviewResponse, IngestCommitResponse
from app.services.ingestion_service import IngestionService
from app.security.rbac import Role

router = APIRouter(prefix="/ingest", tags=["CSV Ingestion"])


@router.post("/preview", response_model=IngestPreviewResponse)
async def preview_csv_upload(
    entity_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(require_role_dep(Role.MANAGER))
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported.")
        
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File size exceeds maximum limit (10MB).")
        
    try:
        preview_data = IngestionService.preview_csv(contents, entity_type)
        return IngestPreviewResponse(**preview_data)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process CSV preview: {str(e)}")


@router.post("/commit", response_model=IngestCommitResponse)
async def commit_csv_upload(
    entity_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role_dep(Role.MANAGER))
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported.")
        
    contents = await file.read()
    try:
        commit_data = IngestionService.commit_csv(db, contents, entity_type)
        return IngestCommitResponse(**commit_data)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import CSV: {str(e)}")
