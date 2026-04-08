"""Dashboard endpoints — stats, recent scans, heatmap."""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query

from middleware.auth import get_current_user
from services.scan_store import get_dashboard_stats, get_heatmap_data, get_scans

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
logger = logging.getLogger(__name__)


@router.get("/stats")
def dashboard_stats(user: dict = Depends(get_current_user)):
    """Return full platform statistics."""
    return get_dashboard_stats()


@router.get("/recent-scans")
def recent_scans(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    risk_level: str = Query(default="all"),
    scan_type: str = Query(default="all"),
    user: dict = Depends(get_current_user),
):
    """Return paginated recent scans with optional filters."""
    rl = risk_level if risk_level != "all" else None
    st = scan_type if scan_type != "all" else None
    return get_scans(limit=limit, offset=offset, risk_level=rl, scan_type=st)


@router.get("/heatmap")
def heatmap(user: dict = Depends(get_current_user)):
    """Return lat/lng cluster data for heatmap visualisation."""
    return get_heatmap_data()
