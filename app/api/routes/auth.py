from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import User
from app.api.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.api.deps import get_current_user
from app.security.auth import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.Username == request.username, User.IsActive == True).first()
    if not user or not verify_password(request.password, user.HashedPassword):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
        
    access_token = create_access_token(
        data={"sub": user.Username, "role": user.Role, "user_id": user.UserId}
    )
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        username=user.Username,
        role=user.Role,
        user_id=user.UserId
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return UserResponse(
        user_id=current_user.UserId,
        username=current_user.Username,
        role=current_user.Role,
        full_name=current_user.FullName
    )
