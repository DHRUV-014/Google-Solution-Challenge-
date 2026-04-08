"""In-memory authentication service with JWT tokens."""
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

# Note: sha256_crypt is used here instead of bcrypt because bcrypt 5.x has
# a known incompatibility with passlib 1.7.4. sha256_crypt is secure and
# works reliably across all versions.


load_dotenv()

logger = logging.getLogger(__name__)

_SECRET = os.getenv("JWT_SECRET", "janarogya-secret-key")
_ALGORITHM = "HS256"
_ACCESS_EXPIRE_HOURS = 24
_REFRESH_EXPIRE_DAYS = 7

_pwd_ctx = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

# In-memory stores
_users: dict[str, dict] = {}          # user_id -> user dict
_email_index: dict[str, str] = {}     # email -> user_id
_token_blacklist: set[str] = set()    # blacklisted tokens


def _hash_password(password: str) -> str:
    return _pwd_ctx.hash(password)


def _verify_password(plain: str, hashed: str) -> bool:
    return _pwd_ctx.verify(plain, hashed)


def _create_token(data: dict, expires_delta: timedelta) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    payload["exp"] = expire
    return jwt.encode(payload, _SECRET, algorithm=_ALGORITHM)


def _seed_user(email: str, password: str, name: str, role: str) -> None:
    user_id = str(uuid.uuid4())
    _users[user_id] = {
        "id": user_id,
        "email": email,
        "password_hash": _hash_password(password),
        "name": name,
        "role": role,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "scan_count": 0,
    }
    _email_index[email] = user_id
    logger.info("Seeded demo user: %s (%s)", email, role)


# ── Seed demo users ────────────────────────────────────────────────────────────
_seed_user("admin@janarogya.health", "admin123", "Admin User", "admin")
_seed_user("doctor@janarogya.health", "doctor123", "Dr. Priya Sharma", "doctor")
_seed_user("patient@janarogya.health", "patient123", "Raju Kumar", "patient")


# ── Public API ─────────────────────────────────────────────────────────────────

def register_user(email: str, password: str, name: str, role: str) -> dict:
    """Register a new user. Raises ValueError on duplicates."""
    email = email.lower().strip()
    if email in _email_index:
        raise ValueError("A user with this email already exists.")
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters.")

    user_id = str(uuid.uuid4())
    _users[user_id] = {
        "id": user_id,
        "email": email,
        "password_hash": _hash_password(password),
        "name": name,
        "role": role,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "scan_count": 0,
    }
    _email_index[email] = user_id

    access_token = _create_token(
        {"sub": user_id, "role": role, "type": "access"},
        timedelta(hours=_ACCESS_EXPIRE_HOURS),
    )
    refresh_token = _create_token(
        {"sub": user_id, "role": role, "type": "refresh"},
        timedelta(days=_REFRESH_EXPIRE_DAYS),
    )
    logger.info("Registered new user: %s (%s)", email, role)
    return {"user_id": user_id, "token": access_token, "refresh_token": refresh_token}


def login_user(email: str, password: str) -> dict:
    """Authenticate user. Raises ValueError on bad credentials."""
    email = email.lower().strip()
    user_id = _email_index.get(email)
    if not user_id:
        raise ValueError("Invalid email or password.")
    user = _users[user_id]
    if not _verify_password(password, user["password_hash"]):
        raise ValueError("Invalid email or password.")

    access_token = _create_token(
        {"sub": user_id, "role": user["role"], "type": "access"},
        timedelta(hours=_ACCESS_EXPIRE_HOURS),
    )
    refresh_token = _create_token(
        {"sub": user_id, "role": user["role"], "type": "refresh"},
        timedelta(days=_REFRESH_EXPIRE_DAYS),
    )
    user_profile = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
    }
    logger.info("User logged in: %s", email)
    return {
        "user_id": user_id,
        "token": access_token,
        "refresh_token": refresh_token,
        "user_profile": user_profile,
    }


def refresh_token(token: str) -> dict:
    """Issue a new access token from a valid refresh token."""
    try:
        payload = jwt.decode(token, _SECRET, algorithms=[_ALGORITHM])
    except JWTError as exc:
        raise ValueError(f"Invalid or expired refresh token: {exc}")
    if payload.get("type") != "refresh":
        raise ValueError("Token is not a refresh token.")
    if token in _token_blacklist:
        raise ValueError("Token has been revoked.")

    user_id = payload.get("sub")
    if not user_id or user_id not in _users:
        raise ValueError("User not found.")

    user = _users[user_id]
    new_access = _create_token(
        {"sub": user_id, "role": user["role"], "type": "access"},
        timedelta(hours=_ACCESS_EXPIRE_HOURS),
    )
    return {"token": new_access}


def logout_user(token: str) -> bool:
    """Blacklist the given token."""
    _token_blacklist.add(token)
    return True


def get_user_from_token(token: str) -> Optional[dict]:
    """Decode token and return user dict, or None if invalid."""
    try:
        payload = jwt.decode(token, _SECRET, algorithms=[_ALGORITHM])
    except JWTError:
        return None
    if token in _token_blacklist:
        return None
    if payload.get("type") != "access":
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    return _users.get(user_id)


def get_all_users() -> list[dict]:
    """Return all users without password hashes."""
    result = []
    for u in _users.values():
        safe = {k: v for k, v in u.items() if k != "password_hash"}
        result.append(safe)
    return result


def update_user_scan_count(user_id: str) -> None:
    """Increment scan count for the given user."""
    if user_id in _users:
        _users[user_id]["scan_count"] = _users[user_id].get("scan_count", 0) + 1
