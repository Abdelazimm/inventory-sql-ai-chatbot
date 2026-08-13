from typing import Optional, List, Dict, Any, Union, Annotated
import operator
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage


class InventorySQLState(TypedDict):
    # LangGraph message history with reducer
    messages: Annotated[List[BaseMessage], operator.add]
    
    # Query lifecycle
    question: str
    intent: Optional[str]               # database_query, chitchat, mutation, unknown
    intent_confidence: Optional[float]
    
    # Text-to-SQL
    sql_query: Optional[str]
    sql_result: Optional[Union[List[Dict[str, Any]], str]]
    
    # Validation & Correction
    is_valid: Optional[bool]
    validation_error: Optional[str]
    execution_error: Optional[str]
    error: Optional[str]
    retries: int
    
    # Observability & Metadata
    request_id: Optional[str]
    session_id: Optional[str]
    user_id: Optional[int]
    user_role: Optional[str]
    execution_time_ms: Optional[float]
    model_name: Optional[str]
