from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.core.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    AuthTokenResponse,
    UserProfileResponse,
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/signup",
    response_model=AuthTokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup(
    request: SignupRequest,
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(
        or_(
            User.email == request.email.lower().strip(),
            User.username == request.username.strip(),
        )
    ).first()
    if existing:
        if existing.email == request.email.lower().strip():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email address already exists.",
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this username already exists.",
        )

    user = User(
        email=request.email.lower().strip(),
        username=request.username.strip(),
        hashed_password=hash_password(request.password),
        full_name=request.full_name.strip() if request.full_name else None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": str(user.id), "username": user.username})
    return AuthTokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        email=user.email,
    )


@router.post(
    "/login",
    response_model=AuthTokenResponse,
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    identifier = request.username_or_email.strip().lower()
    user = db.query(User).filter(
        or_(
            User.email == identifier,
            User.username == request.username_or_email.strip(),
        )
    ).first()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )

    token = create_access_token(data={"sub": str(user.id), "username": user.username})
    return AuthTokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        email=user.email,
    )


@router.get(
    "/me",
    response_model=UserProfileResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user
