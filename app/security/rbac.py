from enum import Enum
from typing import List
from fastapi import HTTPException, status


class Role(str, Enum):
    VIEWER = "viewer"
    MANAGER = "manager"
    ADMIN = "admin"


ROLE_HIERARCHY = {
    Role.VIEWER: 1,
    Role.MANAGER: 2,
    Role.ADMIN: 3
}


def check_role_permission(user_role: str, required_role: Role) -> bool:
    user_level = ROLE_HIERARCHY.get(Role(user_role), 0)
    required_level = ROLE_HIERARCHY.get(required_role, 999)
    return user_level >= required_level


def require_role(user_role: str, required_role: Role):
    if not check_role_permission(user_role, required_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Operation requires '{required_role.value}' role or higher. Your role: '{user_role}'"
        )
