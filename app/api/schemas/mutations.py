from typing import Dict, Any, Optional, Union
from pydantic import BaseModel, Field


class MutationCreateRequest(BaseModel):
    action: str = Field(..., description="'create', 'update', or 'delete'")
    entity_type: str = Field(..., description="e.g. 'asset', 'vendor', 'item'")
    entity_id: Optional[Union[str, int]] = None
    fields: Dict[str, Any] = Field(default_factory=dict)


class MutationPreviewResponse(BaseModel):
    action_id: str
    action: str
    entity_type: str
    entity_id: Optional[Union[str, int]] = None
    fields: Dict[str, Any]
    summary: str
    expires_at: str


class MutationExecutionResponse(BaseModel):
    status: str
    message: str
