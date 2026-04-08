"""Scan management endpoints — analyze (multipart), retrieve, history, delete."""
import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from middleware.auth import get_current_user, get_optional_user
from services.ml_service import run_inference
from services.gemini_service import analyze_image_with_gemini
from services.scan_store import get_scan, get_scans, save_scan, soft_delete_scan
from services.centres_service import get_nearby_centres
from services.auth_service import update_user_scan_count

router = APIRouter(prefix="/scan", tags=["scans"])
logger = logging.getLogger(__name__)

_MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/analyze")
async def scan_analyze(
    image: UploadFile = File(...),
    scan_type: str = Form(default="oral"),
    language: str = Form(default="en"),
    user_id: Optional[str] = Form(default=None),
    questions_answers: Optional[str] = Form(default=None),
    lat: Optional[float] = Form(default=None),
    lng: Optional[float] = Form(default=None),
    user: Optional[dict] = Depends(get_optional_user),
):
    """
    Analyze a scan image (multipart/form-data).
    Returns risk assessment, multi-language explanation, and nearest centres.
    """
    # Validate content type
    if image.content_type and not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be an image.",
        )

    image_bytes = await image.read()
    if len(image_bytes) > _MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image must be smaller than 10 MB.",
        )
    if len(image_bytes) < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image data is too small or empty.",
        )

    # Parse symptoms from JSON string
    symptoms: dict = {}
    if questions_answers:
        try:
            symptoms = json.loads(questions_answers)
        except json.JSONDecodeError:
            symptoms = {}

    # Normalise scan type
    if scan_type not in ("oral", "skin"):
        scan_type = "oral"

    # TFLite inference
    risk_level, confidence = run_inference(image_bytes, scan_type)

    # Gemini analysis
    explanation = await analyze_image_with_gemini(
        image_bytes=image_bytes,
        risk_level=risk_level,
        confidence=confidence,
        scan_type=scan_type,
        symptoms=symptoms,
    )

    explanation_dict = {
        "en": explanation.get("en", ""),
        "hi": explanation.get("hi", ""),
        "ta": explanation.get("ta", ""),
        "te": explanation.get("te", ""),
    }
    concern = explanation.get("concern", "")
    action_required = explanation.get("action_required", risk_level == "HIGH_RISK")

    # Nearest centres
    nearest_centres = []
    if lat is not None and lng is not None:
        try:
            nearest_centres = get_nearby_centres(lat, lng, limit=3)
        except Exception as exc:
            logger.warning("Centres lookup failed: %s", exc)

    # Determine effective user_id
    effective_user_id = (user["id"] if user else None) or user_id or "anonymous"

    # Save scan to store
    scan_data = {
        "user_id": effective_user_id,
        "scan_type": scan_type,
        "risk_level": risk_level,
        "confidence": round(confidence, 4),
        "language": language,
        "explanation_en": explanation_dict.get("en", ""),
        "concern": concern,
        "symptoms": symptoms,
        "lat": lat,
        "lng": lng,
    }
    scan_id = save_scan(scan_data)

    # Update user scan count if authenticated
    if user:
        update_user_scan_count(user["id"])
    elif user_id:
        update_user_scan_count(user_id)

    return {
        "scan_id": scan_id,
        "risk_level": risk_level,
        "confidence": round(confidence, 4),
        "explanation": explanation_dict,
        "concern": concern,
        "action_required": action_required,
        "nearest_centres": nearest_centres,
    }


@router.get("/history")
def scan_history(
    user_id: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
):
    """Return paginated scan history for a user."""
    return get_scans(
        user_id=user_id,
        limit=limit,
        offset=offset,
        from_date=from_date,
        to_date=to_date,
    )


@router.get("/{scan_id}")
def get_scan_detail(scan_id: str):
    """Return full scan details by ID."""
    scan = get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found.")
    return scan


@router.delete("/{scan_id}")
def delete_scan(
    scan_id: str,
    user: dict = Depends(get_current_user),
):
    """Soft-delete a scan. Requires authentication."""
    deleted = soft_delete_scan(scan_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found.")
    return {"success": True}
