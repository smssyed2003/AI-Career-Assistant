from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import TokenResponse, UserCreate, UserLogin, UserRead
from app.services.auth_service import AuthService

router = APIRouter()
service = AuthService()


@router.post("/auth/signup", response_model=TokenResponse, summary="Create user account")
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = service.get_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    user = service.create_user(db, user_in)
    return TokenResponse(access_token=service.create_access_token(user), user=user)


@router.post("/auth/login", response_model=TokenResponse, summary="Login user")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = service.authenticate(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenResponse(access_token=service.create_access_token(user), user=user)


@router.get("/auth/me", response_model=UserRead, summary="Get current user")
def me(current_user: User = Depends(get_current_user)):
    return current_user
