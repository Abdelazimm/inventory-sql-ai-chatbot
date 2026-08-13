import io
import csv
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from app.database.models import Asset, Vendor, Item, Site, Location, Customer


ENTITY_SCHEMAS = {
    "assets": {
        "model": Asset,
        "pk": "AssetTag",
        "required_columns": ["AssetTag", "AssetName", "SiteId"],
        "optional_columns": ["LocationId", "SerialNumber", "Category", "Status", "Cost", "PurchaseDate", "VendorId"]
    },
    "vendors": {
        "model": Vendor,
        "pk": "VendorCode",
        "required_columns": ["VendorCode", "VendorName"],
        "optional_columns": ["Email", "Phone", "AddressLine1", "City", "Country"]
    },
    "items": {
        "model": Item,
        "pk": "ItemCode",
        "required_columns": ["ItemCode", "ItemName"],
        "optional_columns": ["Category", "UnitOfMeasure"]
    },
    "sites": {
        "model": Site,
        "pk": "SiteCode",
        "required_columns": ["SiteCode", "SiteName"],
        "optional_columns": ["AddressLine1", "City", "Country", "TimeZone"]
    },
    "locations": {
        "model": Location,
        "pk": "LocationCode",
        "required_columns": ["SiteId", "LocationCode", "LocationName"],
        "optional_columns": ["ParentLocationId"]
    },
    "customers": {
        "model": Customer,
        "pk": "CustomerCode",
        "required_columns": ["CustomerCode", "CustomerName"],
        "optional_columns": ["Email", "Phone", "BillingAddress1", "BillingCity", "BillingCountry"]
    }
}


def _read_csv_dicts(file_content: bytes) -> tuple[List[str], List[Dict[str, Any]]]:
    text_content = file_content.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text_content))
    columns = reader.fieldnames or []
    rows = [row for row in reader]
    return list(columns), rows


class IngestionService:
    @staticmethod
    def preview_csv(file_content: bytes, entity_type: str) -> Dict[str, Any]:
        entity_key = entity_type.lower()
        if entity_key not in ENTITY_SCHEMAS:
            raise ValueError(f"Unsupported entity type: '{entity_type}'. Allowed: {list(ENTITY_SCHEMAS.keys())}")
            
        schema_info = ENTITY_SCHEMAS[entity_key]
        
        try:
            cols, rows = _read_csv_dicts(file_content)
        except Exception as e:
            raise ValueError(f"Failed to parse CSV file: {str(e)}")
            
        # Check column presence
        missing_required = [col for col in schema_info["required_columns"] if col not in cols]
        preview_rows = rows[:10]
        
        return {
            "entity_type": entity_key,
            "total_rows": len(rows),
            "columns_found": cols,
            "missing_required_columns": missing_required,
            "is_valid": len(missing_required) == 0,
            "preview": preview_rows
        }

    @staticmethod
    def commit_csv(db: Session, file_content: bytes, entity_type: str) -> Dict[str, Any]:
        entity_key = entity_type.lower()
        if entity_key not in ENTITY_SCHEMAS:
            raise ValueError(f"Unsupported entity type: '{entity_type}'")
            
        schema_info = ENTITY_SCHEMAS[entity_key]
        model_cls = schema_info["model"]
        pk_field = schema_info["pk"]
        
        cols, rows = _read_csv_dicts(file_content)
        missing = [col for col in schema_info["required_columns"] if col not in cols]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
            
        inserted = 0
        updated = 0
        rejected = 0
        errors = []
        
        # Ingestion transaction
        try:
            for idx, row in enumerate(rows):
                row_dict = {k: (v.strip() if isinstance(v, str) and v.strip() != "" else None) for k, v in row.items()}
                pk_val = row_dict.get(pk_field)
                
                if not pk_val:
                    rejected += 1
                    errors.append(f"Row {idx + 1}: Missing primary key '{pk_field}'")
                    continue
                
                # Check for existing record
                existing = db.query(model_cls).filter(getattr(model_cls, pk_field) == pk_val).first()
                
                # Filter to only valid model columns
                valid_fields = {k: v for k, v in row_dict.items() if hasattr(model_cls, k)}
                
                if existing:
                    for k, v in valid_fields.items():
                        setattr(existing, k, v)
                    updated += 1
                else:
                    new_record = model_cls(**valid_fields)
                    db.add(new_record)
                    inserted += 1
                    
            db.commit()
            return {
                "entity_type": entity_key,
                "total_processed": len(rows),
                "inserted": inserted,
                "updated": updated,
                "rejected": rejected,
                "errors": errors
            }
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Database error during ingestion: {str(e)}")
