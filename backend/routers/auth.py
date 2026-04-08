"""Authentication endpoints — register, login, refresh, logout, me, google."""
import logging
import re
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, field_validator

from middleware.auth import get_current_user
from services.auth_service import (
    get_user_from_token,
    login_user,
    logout_user,
    refresh_token,
    register_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)
_bearer = HTTPBearer(auto_error=False)

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


# ── Pydantic models ────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    role: str = "patient"

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not _EMAIL_RE.match(v):
            raise ValueError("Invalid email format.")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters.")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ("patient", "doctor", "admin"):
            raise ValueError("role must be 'patient', 'doctor', or 'admin'.")
        return v


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class GoogleAuthRequest(BaseModel):
    id_token: str


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest):
    """Register a new user. Returns tokens."""
    try:
        result = register_user(req.email, req.password, req.name, req.role)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return result


@router.post("/login")
def login(req: LoginRequest):
    """Authenticate and return tokens + profile."""
    try:
        result = login_user(req.email.strip().lower(), req.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return result


@router.post("/refresh")
def token_refresh(req: RefreshRequest):
    """Exchange a refresh token for a new access token."""
    try:
        result = refresh_token(req.refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return result


@router.post("/logout")
def logout(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
):
    """Blacklist the current access token."""
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided.")
    logout_user(credentials.credentials)
    return {"success": True}


@router.get("/me")
def me(user: dict = Depends(get_current_user)):
    """Return current user profile (no password)."""
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "scan_count": user.get("scan_count", 0),
        "created_at": user.get("created_at"),
    }


@router.post("/google")
def google_auth(req: GoogleAuthRequest):
    """Mock Google OAuth — generates a user from the id_token claim."""
    # In production this would verify the Google token.
    # For now, extract or generate an email from the token string.
    fake_uid = str(uuid.uuid4())[:8]
    fake_email = f"google_{fake_uid}@janarogya.health"
    fake_name = "Google User"

    try:
        result = register_user(fake_email, fake_uid + "password", fake_name, "patient")
    except ValueError:
        # Already exists (won't happen with UUID but guard anyway)
        result = login_user(fake_email, fake_uid + "password")

    logger.info("Google auth mock: created user %s", fake_email)
    return {"user_id": result["user_id"], "token": result["token"]}
