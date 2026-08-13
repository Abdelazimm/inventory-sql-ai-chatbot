from typing import Literal, Optional, Dict, Any, Union
from pydantic import BaseModel, Field


class IntentResult(BaseModel):
    """Structured classification of user intent."""
    intent: Literal["database_query", "chitchat", "mutation", "unknown"] = Field(
        description="The primary intent of the user message."
    )
    confidence: float = Field(
        default=1.0, ge=0.0, le=1.0,
        description="Confidence score between 0.0 and 1.0."
    )
    explanation: Optional[str] = Field(
        default=None,
        description="Brief reasoning for the classification."
    )


class SQLGenerationResult(BaseModel):
    """Structured SQL generation output."""
    query: str = Field(
        description="The generated raw SQL query string to be executed."
    )
    operation: Literal["select"] = Field(
        default="select",
        description="Operation type, must be 'select' for analytical queries."
    )
    thought_process: Optional[str] = Field(
        default=None,
        description="Internal query planning notes."
    )


class SQLCorrectionResult(BaseModel):
    """Structured SQL correction output."""
    query: str = Field(
        description="The corrected SQL query string."
    )
    explanation_of_fix: Optional[str] = Field(
        default=None,
        description="Explanation of what was corrected."
    )


class MutationRequest(BaseModel):
    """Structured intent request for database mutations."""
    action: Literal["create", "update", "delete"]
    entity_type: str = Field(description="Target entity, e.g. Asset, Vendor, Item")
    entity_id: Optional[Union[str, int]] = Field(default=None, description="Primary key or unique code if update/delete")
    fields: Dict[str, Any] = Field(default_factory=dict, description="Fields to create or update")
    confirmation_required: bool = Field(default=True)
