import pytest
from app.security.auth import get_password_hash, verify_password, create_access_token, decode_access_token
from app.security.rbac import Role, check_role_permission


def test_password_hashing():
    plain = "secretPassword123"
    hashed = get_password_hash(plain)
    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("wrongPassword", hashed) is False


def test_jwt_token_flow():
    payload = {"sub": "testuser", "role": "manager", "user_id": 42}
    token = create_access_token(payload)
    assert isinstance(token, str)
    
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "testuser"
    assert decoded["role"] == "manager"
    assert decoded["user_id"] == 42


def test_rbac_permissions():
    # Admin can do everything
    assert check_role_permission("admin", Role.VIEWER) is True
    assert check_role_permission("admin", Role.MANAGER) is True
    assert check_role_permission("admin", Role.ADMIN) is True
    
    # Manager can view and manage, not admin
    assert check_role_permission("manager", Role.VIEWER) is True
    assert check_role_permission("manager", Role.MANAGER) is True
    assert check_role_permission("manager", Role.ADMIN) is False
    
    # Viewer can only view
    assert check_role_permission("viewer", Role.VIEWER) is True
    assert check_role_permission("viewer", Role.MANAGER) is False
    assert check_role_permission("viewer", Role.ADMIN) is False
