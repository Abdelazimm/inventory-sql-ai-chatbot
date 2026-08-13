from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import User
from app.api.deps import get_current_user, require_role_dep
from app.api.schemas.mutations import (
    MutationCreateRequest, MutationPreviewResponse, MutationExecutionResponse
)
from app.services.mutation_service import MutationService, PENDING_MUTATIONS
from app.security.rbac import Role, check_role_permission

router = APIRouter(prefix="/mutations", tags=["Mutations"])


@router.post("/preview", response_model=MutationPreviewResponse)
def preview_mutation(
    request: MutationCreateRequest,
    current_user: User = Depends(get_current_user)
):
    # Viewer cannot initiate mutations
    if current_user.Role == Role.VIEWER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Viewer role cannot request mutations.")
        
    # Delete requires admin
    if request.action.lower() == "delete" and current_user.Role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Delete mutations require Admin role.")
        
    try:
        preview = MutationService.create_preview(
            action=request.action,
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            fields=request.fields,
            user_id=current_user.UserId
        )
        return MutationPreviewResponse(**preview)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.post("/{action_id}/confirm", response_model=MutationExecutionResponse)
def confirm_mutation(
    action_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if action_id not in PENDING_MUTATIONS:
        raise HTTPException(status_code=404, detail="Mutation action not found or expired.")
        
    mutation = PENDING_MUTATIONS[action_id]
    if mutation["action"] == "delete" and not check_role_permission(current_user.Role, Role.ADMIN):
        raise HTTPException(status_code=403, detail="Only Admins can confirm deletion.")
        
    try:
        result = MutationService.confirm_mutation(db, action_id, current_user.UserId)
        return MutationExecutionResponse(**result)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mutation execution failed: {str(e)}")


@router.post("/{action_id}/cancel")
def cancel_mutation(action_id: str, current_user: User = Depends(get_current_user)):
    return MutationService.cancel_mutation(action_id)
