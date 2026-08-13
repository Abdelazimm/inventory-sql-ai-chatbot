from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class IngestPreviewResponse(BaseModel):
    entity_type: str
    total_rows: int
    columns_found: List[str]
    missing_required_columns: List[str]
    is_valid: bool
    preview: List[Dict[str, Any]]


class IngestCommitResponse(BaseModel):
    entity_type: str
    total_processed: int
    inserted: int
    updated: int
    rejected: int
    errors: List[str]
