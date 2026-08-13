import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database.models import Asset, Vendor, Item, Site, Location, Customer

# In-memory pending mutation store (or cache)
PENDING_MUTATIONS: Dict[str, Dict[str, Any]] = {}

MODEL_MAP = {
    "asset": (Asset, "AssetTag"),
    "vendor": (Vendor, "VendorCode"),
    "item": (Item, "ItemCode"),
    "site": (Site, "SiteCode"),
    "location": (Location, "LocationCode"),
    "customer": (Customer, "CustomerCode")
}


class MutationService:
    @staticmethod
    def create_preview(action: str, entity_type: str, entity_id: Optional[Any], fields: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        entity_key = entity_type.lower()
        if entity_key not in MODEL_MAP:
            raise ValueError(f"Unsupported entity type for mutation: '{entity_type}'")
            
        action_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(minutes=15)
        
        mutation_data = {
            "action_id": action_id,
            "action": action.lower(),
            "entity_type": entity_key,
            "entity_id": entity_id,
            "fields": fields,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at.isoformat(),
            "status": "pending"
        }
        
        PENDING_MUTATIONS[action_id] = mutation_data
        
        return {
            "action_id": action_id,
            "action": action,
            "entity_type": entity_key,
            "entity_id": entity_id,
            "fields": fields,
            "summary": f"Please confirm {action.upper()} operation on {entity_key} (ID: {entity_id})",
            "expires_at": expires_at.isoformat()
        }

    @staticmethod
    def confirm_mutation(db: Session, action_id: str, user_id: int) -> Dict[str, Any]:
        if action_id not in PENDING_MUTATIONS:
            raise ValueError("Mutation request not found or has expired.")
            
        mutation = PENDING_MUTATIONS[action_id]
        
        model_cls, pk_col = MODEL_MAP[mutation["entity_type"]]
        action = mutation["action"]
        entity_id = mutation["entity_id"]
        fields = mutation["fields"]
        
        try:
            if action == "create":
                new_item = model_cls(**fields)
                db.add(new_item)
                db.commit()
                db.refresh(new_item)
                res = {"status": "success", "message": f"Successfully created {mutation['entity_type']}"}
            elif action == "update":
                item = db.query(model_cls).filter(getattr(model_cls, pk_col) == entity_id).first()
                if not item:
                    raise ValueError(f"{mutation['entity_type']} with ID '{entity_id}' not found.")
                for k, v in fields.items():
                    if hasattr(item, k):
                        setattr(item, k, v)
                db.commit()
                res = {"status": "success", "message": f"Successfully updated {mutation['entity_type']} '{entity_id}'"}
            elif action == "delete":
                item = db.query(model_cls).filter(getattr(model_cls, pk_col) == entity_id).first()
                if not item:
                    raise ValueError(f"{mutation['entity_type']} with ID '{entity_id}' not found.")
                db.delete(item)
                db.commit()
                res = {"status": "success", "message": f"Successfully deleted {mutation['entity_type']} '{entity_id}'"}
            else:
                raise ValueError(f"Unknown action: '{action}'")
                
            del PENDING_MUTATIONS[action_id]
            return res
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Failed to execute mutation: {str(e)}")

    @staticmethod
    def cancel_mutation(action_id: str) -> Dict[str, str]:
        if action_id in PENDING_MUTATIONS:
            del PENDING_MUTATIONS[action_id]
            return {"status": "cancelled", "message": "Mutation request was cancelled."}
        return {"status": "not_found", "message": "Mutation request was not found or already processed."}
