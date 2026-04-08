"""Notification endpoints — follow-up reminders and appointment confirmations."""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/notify", tags=["notifications"])
logger = logging.getLogger(__name__)


class FollowUpRequest(BaseModel):
    user_hash: str
    days_since_scan: int
    risk_level: str


class AppointmentRequest(BaseModel):
    user_hash: str
    centre_name: str
    appointment_date: str


def _send_whatsapp_message(user_hash: str, message: str) -> bool:
    """Attempt to send a WhatsApp message via the whatsapp service."""
    try:
        import httpx, os
        wa_token = os.getenv("WHATSAPP_TOKEN", "")
        wa_phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
        if not wa_token or not wa_phone_id:
            logger.warning("WhatsApp credentials not configured — notification skipped")
            return False
        # user_hash is treated as the recipient phone number
        url = f"https://graph.facebook.com/v18.0/{wa_phone_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": user_hash,
            "type": "text",
            "text": {"body": message},
        }
        response = httpx.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {wa_token}"},
            timeout=10,
        )
        response.raise_for_status()
        logger.info("WhatsApp notification sent to %s", user_hash)
        return True
    except Exception as exc:
        logger.warning("WhatsApp send failed: %s", exc)
        return False


@router.post("/followup")
def send_followup(req: FollowUpRequest):
    """Send a follow-up reminder to a patient."""
    messages = {
        "HIGH_RISK": (
            f"JanArogya Reminder: It has been {req.days_since_scan} days since your screening. "
            "Your result required attention. Please visit a doctor as soon as possible."
        ),
        "LOW_RISK": (
            f"JanArogya Reminder: {req.days_since_scan} days have passed since your screening. "
            "Everything looked good! Remember to do regular self-checks."
        ),
    }
    message = messages.get(
        req.risk_level,
        f"JanArogya: Reminder about your health screening {req.days_since_scan} days ago.",
    )

    sent = _send_whatsapp_message(req.user_hash, message)
    return {
        "sent": sent,
        "message": message if sent else "Notification queued (WhatsApp not configured).",
    }


@router.post("/appointment")
def send_appointment(req: AppointmentRequest):
    """Send an appointment confirmation to a patient."""
    message = (
        f"JanArogya: Your appointment at {req.centre_name} is confirmed for {req.appointment_date}. "
        "Please bring a valid ID and your JanArogya screening report."
    )
    sent = _send_whatsapp_message(req.user_hash, message)
    return {"sent": sent}
