import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.models import ChatSession


class SessionService:
    @staticmethod
    def create_session(db: Session, user_id: Optional[int] = None, title: str = "New Conversation") -> ChatSession:
        session_id = str(uuid.uuid4())
        session = ChatSession(
            SessionId=session_id,
            UserId=user_id,
            Title=title
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_session(db: Session, session_id: str, user_id: Optional[int] = None) -> Optional[ChatSession]:
        query = db.query(ChatSession).filter(ChatSession.SessionId == session_id)
        if user_id is not None:
            query = query.filter(ChatSession.UserId == user_id)
        return query.first()

    @staticmethod
    def list_sessions(db: Session, user_id: Optional[int] = None) -> List[ChatSession]:
        query = db.query(ChatSession)
        if user_id is not None:
            query = query.filter(ChatSession.UserId == user_id)
        return query.order_by(ChatSession.UpdatedAt.desc()).all()

    @staticmethod
    def delete_session(db: Session, session_id: str, user_id: Optional[int] = None) -> bool:
        session = SessionService.get_session(db, session_id, user_id)
        if session:
            db.delete(session)
            db.commit()
            return True
        return False
