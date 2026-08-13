import pytest
from app.services.ingestion_service import IngestionService
from app.database.models import Vendor, Asset


def test_csv_preview_valid():
    csv_data = b"VendorCode,VendorName,Email\nV099,Omega Supply,omega@supply.com"
    preview = IngestionService.preview_csv(csv_data, "vendors")
    assert preview["is_valid"] is True
    assert preview["total_rows"] == 1
    assert preview["missing_required_columns"] == []


def test_csv_preview_missing_columns():
    csv_data = b"SomeOtherColumn,Value\n123,ABC"
    preview = IngestionService.preview_csv(csv_data, "vendors")
    assert preview["is_valid"] is False
    assert "VendorCode" in preview["missing_required_columns"]


def test_csv_commit_transactional(db_session):
    csv_data = b"VendorCode,VendorName,Email\nV101,Titan Industrial,titan@ind.com\nV102,Apex Corp,apex@corp.com"
    res = IngestionService.commit_csv(db_session, csv_data, "vendors")
    assert res["inserted"] == 2
    assert res["rejected"] == 0

    v = db_session.query(Vendor).filter(Vendor.VendorCode == "V101").first()
    assert v is not None
    assert v.VendorName == "Titan Industrial"
