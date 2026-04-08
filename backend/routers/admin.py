"""Admin endpoints — users, system health, broadcast."""
import logging
import os
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from middleware.auth import require_role
from services.auth_service import get_all_users

router = APIRouter(prefix="/admin", tags=["admin"])
logger = logging.getLogger(__name__)

# startup_time is set by main.py after app creation
_startup_time: Optional[float] = None


def set_startup_time(t: float) -> None:
    global _startup_time
    _startup_time = t


_admin_only = require_role("admin")


class BroadcastRequest(BaseModel):
    message: str
    language: str = "en"
    target: str = "all"  # "all" | "high_risk"


@router.get("/users")
def list_users(user: dict = Depends(_admin_only)):
    """Return all registered users (no passwords)."""
    return get_all_users()


@router.get("/system-health")
def system_health(user: dict = Depends(_admin_only)):
    """Return API and service health indicators."""
    # Check model files
    from services.ml_service import _MODEL_PATHS
    oral_ok = os.path.exists(_MODEL_PATHS.get("oral", ""))
    skin_ok = os.path.exists(_MODEL_PATHS.get("skin", ""))

    # Check Firebase
    try:
        from services.firebase_service import _firebase_ready
        firebase_ok = bool(_firebase_ready)
    except Exception:
        firebase_ok = False

    uptime = round(time.time() - _startup_time, 1) if _startup_time else 0.0

    return {
        "api_status": "ok",
        "model_status": {"oral": oral_ok, "skin": skin_ok},
        "firebase_status": firebase_ok,
        "uptime_seconds": uptime,
        "version": "1.0.0",
        "last_errors": [],
    }


@router.post("/broadcast")
def broadcast(req: BroadcastRequest, user: dict = Depends(_admin_only)):
    """Queue a broadcast message to users."""
    if req.target not in ("all", "high_risk"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="target must be 'all' or 'high_risk'.",
        )

    from services.scan_store import _scans

    if req.target == "high_risk":
        recipients = {
            s["user_id"] for s in _scans
            if not s.get("deleted") and s.get("risk_level") == "HIGH_RISK"
        }
    else:
        recipients = {s["user_id"] for s in _scans if not s.get("deleted")}

    queued = len(recipients)
    logger.info(
        "Admin broadcast queued: target=%s lang=%s recipients=%d msg=%.60s",
        req.target, req.language, queued, req.message,
    )
    return {"queued": queued, "success": True}
