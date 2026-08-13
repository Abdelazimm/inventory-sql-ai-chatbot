import pytest
from app.agents.schema import get_dynamic_schema, get_schema_dict
from tests.conftest import test_engine


def test_dynamic_schema_generation():
    schema_str = get_dynamic_schema(test_engine)
    assert "Table: Assets" in schema_str
    assert "AssetTag" in schema_str
    assert "PRIMARY KEY" in schema_str
    assert "Foreign Keys:" in schema_str
    assert "Assets.(VendorId) -> Vendors.(VendorId)" in schema_str or "Vendors" in schema_str


def test_schema_dict():
    schema_dict = get_schema_dict(test_engine)
    assert "Assets" in schema_dict
    assert "Vendors" in schema_dict
    assert "Items" in schema_dict
    
    asset_cols = [c["name"] for c in schema_dict["Assets"]["columns"]]
    assert "AssetTag" in asset_cols
    assert "Cost" in asset_cols
    assert "SiteId" in asset_cols
