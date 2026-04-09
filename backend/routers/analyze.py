"""REST endpoint used by the Flutter app for combined TFLite + Gemini analysis."""
import base64
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.gemini_service import (
    DISCLAIMER,
    SYMPTOM_QUESTIONS,
    analyze_image_with_gemini,
    check_image_quality,
)
from services.ml_service import run_inference

router = APIRouter()
logger = logging.getLogger(__name__)


class AnalyzeRequest(BaseModel):
    image_base64: str
    scan_type: str          # "oral" | "skin" | "other"
    symptoms: Optional[dict] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@router.post("/analyze")
async def analyze(req: AnalyzeRequest):
    """
    Analyze an image and return risk level with 4-language explanation.

    Response:
    {
        "risk_level": "LOW_RISK" | "HIGH_RISK" | "INVALID",
        "confidence": 0.0-1.0,
        "explanation": {"en": "...", "hi": "...", "ta": "...", "te": "..."},
        "nearest_centers": [],
        "disclaimer": {"en": "...", "hi": "...", "ta": "...", "te": "..."}
    }
    """
    # Validate scan type
    scan_type = req.scan_type if req.scan_type in ("oral", "skin") else "oral"

    # Decode image
    try:
        image_bytes = base64.b64decode(req.image_base64)
        if len(image_bytes) < 100:
            return _error_response("Image data is too small or invalid.")
    except Exception:
        return _error_response("Invalid base64 image data.")

    # TFLite on-server inference
    risk_level, confidence = run_inference(image_bytes, scan_type)

    # Gemini holistic analysis (image + model result + symptoms)
    explanation = await analyze_image_with_gemini(
        image_bytes=image_bytes,
        risk_level=risk_level,
        confidence=confidence,
        scan_type=scan_type,
        symptoms=req.symptoms,
    )

    # Build 4-language explanation dict
    explanation_dict = {
        "en": explanation.get("en", ""),
        "hi": explanation.get("hi", ""),
        "ta": explanation.get("ta", ""),
        "te": explanation.get("te", ""),
    }

    # Nearest centers (requires lat/lng — return empty if not provided)
    nearest_centers = []
    if req.latitude and req.longitude:
        try:
            from services.maps_service import find_nearest_cancer_center
            nearest_centers = await find_nearest_cancer_center(
                req.latitude, req.longitude
            )
        except Exception as exc:
            logger.warning("Maps lookup failed: %s", exc)

    return {
        "risk_level": risk_level,
        "confidence": round(confidence, 4),
        "explanation": explanation_dict,
        "nearest_centers": nearest_centers,
        "disclaimer": DISCLAIMER,
    }


@router.get("/symptoms/{scan_type}")
def get_symptom_questions(scan_type: str):
    """Return the bilingual symptom questionnaire for a given scan type."""
    if scan_type not in ("oral", "skin"):
        raise HTTPException(400, "scan_type must be 'oral' or 'skin'")
    return {"questions": SYMPTOM_QUESTIONS[scan_type]}


class FollowupRequest(BaseModel):
    scan_type: str
    selected_symptoms: list[str] = []
    duration: str = ""
    pain_level: int = 0
    risk_factors: list[str] = []


@router.post("/symptoms/followup")
async def get_followup_questions(req: FollowupRequest):
    """Use Gemini to generate personalised follow-up questions based on patient's symptom profile."""
    import json
    import re
    import os
    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))

    symptoms_str = ", ".join(req.selected_symptoms) if req.selected_symptoms else "none specified"
    risk_str = ", ".join(req.risk_factors) if req.risk_factors else "none"
    pain_desc = "no pain" if req.pain_level == 0 else f"pain level {req.pain_level}/10"

    prompt = f"""You are an expert medical screening assistant specialising in early cancer detection in India.

A patient is undergoing a {req.scan_type} cancer screening with the following profile:
- Symptoms selected: {symptoms_str}
- Duration: {req.duration or "not specified"}
- {pain_desc}
- Risk factors: {risk_str}

Generate exactly 2 highly specific, clinically relevant follow-up questions tailored to THIS patient's exact symptom profile.
Questions must be:
- In plain, simple English understandable by rural Indian patients
- Directly relevant to the symptoms listed above
- Designed to help a doctor assess urgency and severity
- Different every time — do not use generic questions

Return ONLY valid JSON with no markdown: {{"questions": ["question 1", "question 2"]}}"""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        text = response.text.strip()
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            data = json.loads(match.group())
            if isinstance(data.get("questions"), list) and len(data["questions"]) >= 2:
                return {"questions": data["questions"][:2]}
    except Exception as exc:
        logger.warning("Gemini followup failed: %s", exc)

    # Scan-type specific fallbacks
    fallbacks = {
        "oral": [
            "Have you noticed difficulty opening your mouth or moving your tongue freely?",
            "Have any of these sores or patches been present for more than 3 weeks without healing?",
        ],
        "skin": [
            "Has the lesion changed in size, shape, or colour in the last 4 weeks?",
            "Does the area bleed spontaneously or when touched lightly?",
        ],
    }
    return {"questions": fallbacks.get(req.scan_type, [
        "Have you seen a doctor about these symptoms before?",
        "Are you currently taking any medications that affect your immune system?",
    ])}


def _error_response(message: str) -> dict:
    """Return a safe error response that never crashes the app."""
    return {
        "risk_level": "INVALID",
        "confidence": 0.0,
        "explanation": {
            "en": f"Analysis failed: {message} Please retake the photo and try again.",
            "hi": f"जांच विफल: {message} कृपया फोटो दोबारा लें।",
            "ta": f"பகுப்பாய்வு தோல்வியடைந்தது: {message} மீண்டும் புகைப்படம் எடுக்கவும்.",
            "te": f"విశ్లేషణ విఫలమైంది: {message} దయచేసి ఫోటో తిరిగి తీయండి.",
        },
        "nearest_centers": [],
        "disclaimer": DISCLAIMER,
    }
