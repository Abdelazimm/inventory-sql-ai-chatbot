import pytest
from app.services.session_service import SessionService
from app.database.models import ChatSession


def test_session_crud_and_isolation(db_session):
    # User 1 creates a session
    s1 = SessionService.create_session(db_session, user_id=1, title="User 1 Session")
    assert s1.SessionId is not None

    # User 2 creates a session
    s2 = SessionService.create_session(db_session, user_id=2, title="User 2 Session")
    assert s2.SessionId != s1.SessionId

    # Listing user 1 sessions does not leak user 2
    u1_sessions = SessionService.list_sessions(db_session, user_id=1)
    u1_ids = [s.SessionId for s in u1_sessions]
    assert s1.SessionId in u1_ids
    assert s2.SessionId not in u1_ids

    # Delete session
    deleted = SessionService.delete_session(db_session, s1.SessionId, user_id=1)
    assert deleted is True
    assert SessionService.get_session(db_session, s1.SessionId) is None
