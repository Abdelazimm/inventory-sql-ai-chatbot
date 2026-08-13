from typing import Optional, Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import User
from app.security.auth import decode_access_token
from app.security.rbac import Role, check_role_permission

security_scheme = HTTPBearer(auto_error=False)


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    if not credentials:
        return None
    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        return None
    username = payload["sub"]
    user = db.query(User).filter(User.Username == username, User.IsActive == True).first()
    return user


def get_current_user(
    user: Optional[User] = Depends(get_current_user_optional)
) -> User:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


def require_role_dep(required_role: Role):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if not check_role_permission(current_user.Role, required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires '{required_role.value}' role. Your role is '{current_user.Role}'."
            )
        return current_user
    return role_checker
