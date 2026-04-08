"""Cancer screening centres endpoints."""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from middleware.auth import require_role
from services.centres_service import add_centre, get_all_centres, get_nearby_centres

router = APIRouter(prefix="/centres", tags=["centres"])
logger = logging.getLogger(__name__)


class CentreRequest(BaseModel):
    name: str
    address: str
    city: str
    state: str
    lat: float
    lng: float
    phone: str
    type: str


@router.get("/nearby")
def nearby_centres(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius_km: float = Query(default=50.0, ge=1, le=500),
    limit: int = Query(default=5, ge=1, le=20),
):
    """Return nearest cancer screening centres."""
    centres = get_nearby_centres(lat=lat, lng=lng, radius_km=radius_km, limit=limit)
    return {"centres": centres, "total": len(centres)}


@router.get("/all")
def all_centres():
    """Return all known cancer screening centres."""
    centres = get_all_centres()
    return {"centres": centres, "total": len(centres)}


@router.post("/add", status_code=status.HTTP_201_CREATED)
def add_new_centre(
    req: CentreRequest,
    user: dict = Depends(require_role("admin")),
):
    """Add a new cancer screening centre (admin only)."""
    centre_id = add_centre(req.model_dump())
    logger.info("Admin %s added centre: %s", user["id"], req.name)
    return {"centre_id": centre_id}
