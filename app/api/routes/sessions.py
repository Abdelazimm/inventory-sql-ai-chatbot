from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import User
from app.api.deps import get_current_user_optional
from app.api.schemas.chat import SessionCreateRequest, SessionResponse
from app.services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("", response_model=SessionResponse)
def create_session(
    request: SessionCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    user_id = current_user.UserId if current_user else None
    session = SessionService.create_session(db, user_id=user_id, title=request.title or "New Conversation")
    return SessionResponse(
        session_id=session.SessionId,
        title=session.Title,
        created_at=session.CreatedAt.isoformat(),
        updated_at=session.UpdatedAt.isoformat()
    )


@router.get("", response_model=List[SessionResponse])
def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    user_id = current_user.UserId if current_user else None
    sessions = SessionService.list_sessions(db, user_id=user_id)
    return [
        SessionResponse(
            session_id=s.SessionId,
            title=s.Title,
            created_at=s.CreatedAt.isoformat(),
            updated_at=s.UpdatedAt.isoformat()
        )
        for s in sessions
    ]


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    user_id = current_user.UserId if current_user else None
    session = SessionService.get_session(db, session_id=session_id, user_id=user_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    return SessionResponse(
        session_id=session.SessionId,
        title=session.Title,
        created_at=session.CreatedAt.isoformat(),
        updated_at=session.UpdatedAt.isoformat()
    )


@router.delete("/{session_id}")
def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    user_id = current_user.UserId if current_user else None
    deleted = SessionService.delete_session(db, session_id=session_id, user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    return {"status": "success", "message": f"Session '{session_id}' deleted successfully."}
