# file: app/api/routers/auth.py
from datetime import UTC, datetime, timedelta
from importlib import import_module
from typing import cast

from fastapi import APIRouter, HTTPException, status

from app.core.settings import settings
from app.schemas.auth import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])
jwt = import_module("jwt")


def _create_access_token(subject: str) -> str:
    expires_delta = timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": subject,
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + expires_delta,
    }
    return cast(
        str,
        jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm),
    )


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    if (
        payload.email != settings.demo_user_email
        or payload.password != settings.demo_user_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = _create_access_token(payload.email)
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.jwt_expire_minutes * 60,
        user_name="山田 太郎",
    )
