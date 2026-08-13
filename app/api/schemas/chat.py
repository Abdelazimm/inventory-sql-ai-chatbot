from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="Natural language question")
    session_id: Optional[str] = Field(default=None, description="UUID session identifier")


class ChatMetadata(BaseModel):
    intent: Optional[str] = None
    generated_sql: Optional[str] = None
    is_valid_sql: Optional[bool] = None
    retry_count: int = 0
    execution_time_ms: Optional[float] = None
    row_count: Optional[int] = None
    model: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    request_id: str
    metadata: Optional[ChatMetadata] = None


class SessionCreateRequest(BaseModel):
    title: Optional[str] = "New Conversation"


class SessionResponse(BaseModel):
    session_id: str
    title: str
    created_at: str
    updated_at: str
