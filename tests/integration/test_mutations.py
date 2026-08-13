import pytest
from app.services.mutation_service import MutationService
from app.database.models import Vendor


def test_mutation_preview_and_confirm(db_session):
    preview = MutationService.create_preview(
        action="create",
        entity_type="vendor",
        entity_id=None,
        fields={"VendorCode": "V555", "VendorName": "Mutation Vendor", "Email": "mut@vendor.com"},
        user_id=1
    )
    assert "action_id" in preview
    action_id = preview["action_id"]

    # Confirm mutation
    res = MutationService.confirm_mutation(db_session, action_id, user_id=1)
    assert res["status"] == "success"

    v = db_session.query(Vendor).filter(Vendor.VendorCode == "V555").first()
    assert v is not None
    assert v.VendorName == "Mutation Vendor"


def test_mutation_cancel():
    preview = MutationService.create_preview(
        action="delete",
        entity_type="vendor",
        entity_id="V555",
        fields={},
        user_id=1
    )
    action_id = preview["action_id"]
    cancel_res = MutationService.cancel_mutation(action_id)
    assert cancel_res["status"] == "cancelled"
