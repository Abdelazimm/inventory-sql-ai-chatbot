import pytest
from app.agents.validator import validate_sql_query


def test_valid_select_queries():
    valid_queries = [
        "SELECT * FROM Assets",
        "SELECT AssetName, Cost FROM Assets WHERE Cost > 1000",
        "SELECT v.VendorName, COUNT(a.AssetId) FROM Vendors v JOIN Assets a ON v.VendorId = a.VendorId GROUP BY v.VendorName",
        "WITH ExpensiveAssets AS (SELECT * FROM Assets WHERE Cost > 1000) SELECT * FROM ExpensiveAssets",
        "SELECT MAX(Cost) AS MaxCost, MIN(Cost) AS MinCost FROM Assets",
        "SELECT * FROM Assets ORDER BY Cost DESC LIMIT 5"
    ]
    for q in valid_queries:
        is_valid, error = validate_sql_query(q)
        assert is_valid is True, f"Expected query to be valid: {q}, error: {error}"
        assert error is None


def test_block_destructive_queries():
    blocked_queries = [
        "DROP TABLE Assets",
        "DELETE FROM Assets WHERE AssetId = 1",
        "UPDATE Assets SET Cost = 0",
        "INSERT INTO Assets (AssetTag, AssetName) VALUES ('TAG-99', 'Fake')",
        "ALTER TABLE Assets ADD COLUMN Hacked TEXT",
        "CREATE TABLE Hack (id INT)",
        "TRUNCATE TABLE Assets"
    ]
    for q in blocked_queries:
        is_valid, error = validate_sql_query(q)
        assert is_valid is False, f"Expected query to be blocked: {q}"
        assert error is not None
        assert "read-only" in error.lower() or "forbidden" in error.lower()


def test_block_stacked_queries():
    stacked_queries = [
        "SELECT * FROM Assets; DROP TABLE Vendors;",
        "SELECT 1; SELECT 2;",
        "SELECT * FROM Items; DELETE FROM Items;"
    ]
    for q in stacked_queries:
        is_valid, error = validate_sql_query(q)
        assert is_valid is False
        assert "multiple" in error.lower() or "forbidden" in error.lower()


def test_block_dangerous_keywords():
    dangerous = [
        "ATTACH DATABASE 'hacked.db' AS hacked",
        "DETACH DATABASE hacked",
        "PRAGMA database_list",
        "SELECT * FROM Assets; VACUUM;"
    ]
    for q in dangerous:
        is_valid, error = validate_sql_query(q)
        assert is_valid is False
        assert "forbidden" in error.lower() or "multiple" in error.lower()
