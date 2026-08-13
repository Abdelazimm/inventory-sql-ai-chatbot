import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage
from app.database.connection import get_db
from app.database.models import User, ChatSession
from app.api.deps import get_current_user_optional
from app.api.schemas.chat import ChatRequest, ChatResponse, ChatMetadata
from app.agents.graph import sql_agent_app
from app.services.session_service import SessionService
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    request_id = str(uuid.uuid4())
    user_id = current_user.UserId if current_user else None
    user_role = current_user.Role if current_user else "viewer"
    
    # Manage session
    session_id = request.session_id
    if not session_id:
        new_session = SessionService.create_session(db, user_id=user_id, title=request.message[:40])
        session_id = new_session.SessionId
    else:
        # Verify session exists, otherwise create
        existing = SessionService.get_session(db, session_id=session_id)
        if not existing:
            SessionService.create_session(db, user_id=user_id, title=request.message[:40])

    # Build LangGraph input state
    config = {"configurable": {"thread_id": session_id}}
    
    state_input = {
        "messages": [HumanMessage(content=request.message)],
        "question": request.message,
        "request_id": request_id,
        "session_id": session_id,
        "user_id": user_id,
        "user_role": user_role,
        "retries": 0,
        "model_name": settings.MODEL_NAME
    }
    
    try:
        final_state = sql_agent_app.invoke(state_input, config=config)
    except Exception as e:
        logger.error(f"LangGraph execution failed for request {request_id}: {str(e)}", exc_info=True)
        return ChatResponse(
            answer="I encountered an unexpected error processing your request. Please try again.",
            session_id=session_id,
            request_id=request_id,
            metadata=ChatMetadata(
                intent="unknown",
                retry_count=0,
                model=settings.MODEL_NAME
            )
        )
        
    # Extract last AI message
    answer = "I was unable to generate an answer."
    if final_state and "messages" in final_state and len(final_state["messages"]) > 0:
        latest_msg = final_state["messages"][-1]
        answer = latest_msg.content
        
    # Build metadata
    sql_result = final_state.get("sql_result")
    row_count = len(sql_result) if isinstance(sql_result, list) else None
    
    metadata = ChatMetadata(
        intent=final_state.get("intent"),
        generated_sql=final_state.get("sql_query"),
        is_valid_sql=final_state.get("is_valid"),
        retry_count=final_state.get("retries", 0),
        execution_time_ms=final_state.get("execution_time_ms"),
        row_count=row_count,
        model=settings.MODEL_NAME
    )
    
    return ChatResponse(
        answer=answer,
        session_id=session_id,
        request_id=request_id,
        metadata=metadata
    )
