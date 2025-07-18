from fastapi import APIRouter, HTTPException, Depends, status
from datetime import timedelta
from sqlalchemy.exc import DataError
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.token import Token
from app.services.auth import get_user_by_username, create_user, authenticate_user
from app.services.security import create_access_token
from app.services import validator
from app.config import settings
from app.db.database import get_db


router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    validator.validate_string_field('username', user.username)
    validator.validate_password(user.password)

    try:
        db_user = get_user_by_username(db, username=user.username)
        if db_user:
            raise HTTPException(
                status_code=400,
                detail="Username already registered"
            )
        return create_user(db, user=user)
    except DataError:
        raise HTTPException(
            status_code=400,
            detail="Invalid data: one or more fields exceed length limits"
        )


@router.post("/login", response_model=Token)
def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    validator.validate_string_field('username', user_credentials.username)
    validator.validate_password(user_credentials.password)

    try:
        user = authenticate_user(db, user_credentials.username, user_credentials.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except DataError:
        raise HTTPException(
            status_code=400,
            detail="Invalid data: one or more fields exceed length limits"
        )
