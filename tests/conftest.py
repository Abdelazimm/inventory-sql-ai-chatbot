import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database.connection import Base, get_db
from app.database.models import User, Customer, Vendor, Site, Location, Item, Asset
from app.security.auth import get_password_hash, create_access_token
from app.main import app

# Create in-memory test database
TEST_DB_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    
    # Seed test users
    admin = User(Username="admin", HashedPassword=get_password_hash("admin123"), Role="admin", FullName="Admin User")
    manager = User(Username="manager", HashedPassword=get_password_hash("manager123"), Role="manager", FullName="Manager User")
    viewer = User(Username="viewer", HashedPassword=get_password_hash("viewer123"), Role="viewer", FullName="Viewer User")
    session.add_all([admin, manager, viewer])

    # Seed test inventory entities
    vendor = Vendor(VendorCode="V001", VendorName="TechCorp", Email="info@techcorp.com")
    site = Site(SiteCode="S01", SiteName="HQ")
    session.add_all([vendor, site])
    session.flush()

    location = Location(SiteId=site.SiteId, LocationCode="HQ-L1", LocationName="Main Room")
    item = Item(ItemCode="ITM-001", ItemName="ThinkPad Laptop", Category="Electronics")
    session.add_all([location, item])
    session.flush()

    asset = Asset(
        AssetTag="TAG-001",
        AssetName="ThinkPad X1",
        SiteId=site.SiteId,
        LocationId=location.LocationId,
        VendorId=vendor.VendorId,
        Cost=1500.0,
        Status="Active"
    )
    session.add(asset)
    session.commit()
    session.close()


@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token():
    return create_access_token({"sub": "admin", "role": "admin", "user_id": 1})


@pytest.fixture
def manager_token():
    return create_access_token({"sub": "manager", "role": "manager", "user_id": 2})


@pytest.fixture
def viewer_token():
    return create_access_token({"sub": "viewer", "role": "viewer", "user_id": 3})
