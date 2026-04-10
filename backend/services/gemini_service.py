"""Google Gemini AI integration — returns 4-language analysis."""
import json
import logging
import os
import re

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

logger = logging.getLogger(__name__)

_API_KEY = os.getenv("GEMINI_API_KEY", "")
if not _API_KEY:
    logger.warning("GEMINI_API_KEY is not set — Gemini calls will fail")
_client = genai.Client(api_key=_API_KEY)
_MODEL = "gemini-2.5-flash"

# ── Symptom questions ──────────────────────────────────────────────────────────

SYMPTOM_QUESTIONS = {
    "oral": [
        {
            "id": "duration",
            "hi": "यह समस्या कितने दिनों से है?",
            "en": "How many days have you had this problem?",
            "ta": "இந்தப் பிரச்சனை எத்தனை நாட்களாக உள்ளது?",
            "te": "ఈ సమస్య ఎన్ని రోజులనుండి ఉంది?",
            "options_hi": ["1-7 दिन", "1-4 हफ्ते", "1 महीने से ज्यादा"],
            "options_en": ["1-7 days", "1-4 weeks", "More than 1 month"],
        },
        {
            "id": "pain",
            "hi": "क्या मुँह में दर्द या जलन है?",
            "en": "Is there pain or burning sensation in the mouth?",
            "ta": "வாயில் வலி அல்லது எரிச்சல் உள்ளதா?",
            "te": "నోటిలో నొప్పి లేదా మంట ఉందా?",
            "options_hi": ["हाँ, बहुत", "थोड़ा", "नहीं"],
            "options_en": ["Yes, severe", "Mild", "No"],
        },
        {
            "id": "patches",
            "hi": "क्या सफेद, लाल, या काले धब्बे दिखते हैं?",
            "en": "Do you see white, red, or dark patches?",
            "ta": "வெள்ளை, சிவப்பு அல்லது கருப்பு திட்டுகள் தெரிகின்றனவா?",
            "te": "తెలుపు, ఎరుపు లేదా చీకటి మచ్చలు కనిపిస్తున్నాయా?",
            "options_hi": ["सफेद धब्बे", "लाल धब्बे", "दोनों", "कोई नहीं"],
            "options_en": ["White patches", "Red patches", "Both", "None"],
        },
    ],
    "skin": [
        {
            "id": "duration",
            "hi": "यह घाव/धब्बा कितने दिनों से है?",
            "en": "How long have you had this wound or spot?",
            "ta": "இந்த புண் அல்லது திட்டு எத்தனை நாட்களாக உள்ளது?",
            "te": "ఈ గాయం లేదా మచ్చ ఎంత కాలం నుండి ఉంది?",
            "options_hi": ["1-7 दिन", "1-4 हफ्ते", "1 महीने से ज्यादा"],
            "options_en": ["1-7 days", "1-4 weeks", "More than 1 month"],
        },
        {
            "id": "pain",
            "hi": "क्या इसमें दर्द, खुजली, या जलन है?",
            "en": "Is there pain, itching, or burning?",
            "ta": "வலி, அரிப்பு அல்லது எரிச்சல் உள்ளதா?",
            "te": "నొప్పి, దురద లేదా మంట ఉందా?",
            "options_hi": ["हाँ, बहुत", "थोड़ा", "नहीं"],
            "options_en": ["Yes, severe", "Mild", "No"],
        },
        {
            "id": "change",
            "hi": "क्या यह बढ़ रहा है या रंग बदल रहा है?",
            "en": "Is it growing in size or changing color?",
            "ta": "இது பெரிதாகுகிறதா அல்லது நிறம் மாறுகிறதா?",
            "te": "ఇది పెద్దదవుతుందా లేదా రంగు మారుతుందా?",
            "options_hi": ["हाँ, बढ़ रहा है", "रंग बदल रहा है", "दोनों", "नहीं"],
            "options_en": ["Yes, growing", "Color changing", "Both", "No change"],
        },
    ],
}

# ── Prompts ────────────────────────────────────────────────────────────────────

_QUESTIONS_PROMPT = """\
You are a medical AI screening assistant. Look at this {scan_type} scan image carefully.
Generate exactly 3 short, clear screening questions to ask this patient about their symptoms.
These must be specific to what you observe in THIS image.

Respond ONLY in this exact JSON format (no markdown):
{{
    "questions": [
        {{
            "id": "q1",
            "en": "English question?",
            "hi": "Hindi question?",
            "ta": "Tamil question?",
            "te": "Telugu question?",
            "options_en": ["Option A", "Option B", "Option C"],
            "options_hi": ["विकल्प A", "विकल्प B", "विकल्प C"],
            "options_ta": ["விருப்பம் A", "விருப்பம் B", "விருப்பம் C"],
            "options_te": ["ఎంపిక A", "ఎంపిక B", "ఎంపిక C"]
        }},
        {{ "id": "q2", ... }},
        {{ "id": "q3", ... }}
    ]
}}

Rules:
- Questions must be specific to what you observe in this image
- Each question must have exactly 3 options
- Options must be translations of each other
- Never mention cancer, tumor, or malignant
- Keep questions simple enough for rural patients
"""

_CHAT_SYSTEM = """\
You are JanArogya Health Assistant, a compassionate AI health guide for rural India.
You help people understand general health topics, symptoms, and when to seek care.
Rules:
- Never diagnose disease
- Never mention cancer, tumor, malignant directly — use "concerning growths" or "abnormal tissue"
- Always recommend seeing a real doctor for serious concerns
- Be warm, simple, and accessible — your users may have low health literacy
- Respond in {language} only
- Keep responses concise (max 4 sentences unless a list is clearly better)
- For emergency symptoms (chest pain, difficulty breathing, heavy bleeding) always say "call emergency services immediately"
"""

_QUALITY_PROMPT = """\
You are a medical image quality checker. Look at this photo and assess if it is suitable for cancer screening.

Check for these problems:
- Severe blur or motion blur
- Very dark or overexposed image
- Wrong body part (not showing mouth/skin as expected)
- Photo of a photo or screenshot
- Unrelated object

Respond ONLY in this exact JSON (no markdown):
{"quality": "GOOD", "reason": ""}
or
{"quality": "BAD", "reason": "one short sentence explaining the problem"}
"""

_ANALYSIS_PROMPT = """\
You are a compassionate AI health guide for rural India. You are looking directly at this {scan_type} scan photo AND the AI model result.

WHAT THE AI MODEL FOUND:
- Risk level: {risk_level} (confidence: {confidence}%)
- Scan type: {scan_type}

WHAT THE PATIENT TOLD US:
{symptoms_text}

YOUR TASK: Look at the actual image and write a personalised, warm explanation.
Describe what you actually see in the image (colour, texture, size of any marks).
Connect it to what the patient reported.
Tell them exactly what to do next in simple words.

ORAL SCAN — look for: white or red patches, sores, unusual textures, swelling
SKIN SCAN — look for: irregular borders, multiple colours, raised areas, size relative to surrounding skin

Respond ONLY in this exact JSON (no markdown, no extra text):
{{
    "en": "3 sentences in plain English. Sentence 1: describe what you literally see in the photo (colour, size, location). Sentence 2: connect to their symptoms. Sentence 3: one clear action step.",
    "hi": "3 सरल हिंदी वाक्य। वाक्य 1: तस्वीर में क्या दिखा (रंग, आकार, जगह)। वाक्य 2: लक्षणों से जोड़ें। वाक्य 3: एक स्पष्ट कदम।",
    "ta": "3 தமிழ் வாக்கியங்கள். வாக்கியம் 1: படத்தில் என்ன தெரிகிறது. வாக்கியம் 2: அறிகுறிகளுடன் இணைக்கவும். வாக்கியம் 3: ஒரு தெளிவான நடவடிக்கை.",
    "te": "3 తెలుగు వాక్యాలు. వాక్యం 1: ఫోటోలో ఏమి కనిపిస్తుందో. వాక్యం 2: లక్షణాలతో అనుసంధానించండి. వాక్యం 3: ఒక స్పష్టమైన చర్య.",
    "concern": "One calm, practical English sentence — the single most important action. E.g. 'Visit your nearest government hospital within 2 days and show them this report.'",
    "action_required": true
}}

Strict rules:
- NEVER use: cancer, tumor, malignant, lesion, biopsy, pathology, carcinoma, oncology
- Use instead: area, spot, patch, mark, change, growth, tissue
- LOW_RISK: reassure warmly, say the area looks mostly normal, advise monitoring — calm tone
- HIGH_RISK or MEDIUM_RISK: urge doctor visit urgently but calmly — within 1-2 days
- INVALID: explain photo issue simply, ask them to retake with good lighting
- action_required = true if HIGH_RISK, MEDIUM_RISK, or symptoms show >1 month duration or severe pain
"""

# ── Fallbacks ──────────────────────────────────────────────────────────────────

_FALLBACK = {
    "en": "Your image has been reviewed. Some areas need attention. Please consult a qualified doctor for proper evaluation.",
    "hi": "आपकी तस्वीर देखी गई है। कुछ क्षेत्रों पर ध्यान देने की जरूरत है। कृपया एक योग्य डॉक्टर से मिलें।",
    "ta": "உங்கள் படம் பரிசீலிக்கப்பட்டது. சில பகுதிகளுக்கு கவனம் தேவை. தகுதியான மருத்துவரை அணுகவும்.",
    "te": "మీ చిత్రం సమీక్షించబడింది. కొన్ని ప్రాంతాలకు శ్రద్ధ అవసరం. అర్హత గల వైద్యుడిని సంప్రదించండి.",
    "action_required": True,
}

_ERROR = {
    "en": "Screening encountered an issue. Please consult a doctor.",
    "hi": "जांच में समस्या हुई। कृपया डॉक्टर से सलाह लें।",
    "ta": "திரையிடலில் சிக்கல் ஏற்பட்டது. மருத்துவரை அணுகவும்.",
    "te": "స్క్రీనింగ్‌లో సమస్య వచ్చింది. వైద్యుడిని సంప్రదించండి.",
    "action_required": True,
}

DISCLAIMER = {
    "en": "This is an AI screening tool, not a medical diagnosis. Please consult a qualified doctor.",
    "hi": "यह एक AI स्क्रीनिंग टूल है, कोई डॉक्टरी निदान नहीं। कृपया किसी योग्य डॉक्टर से मिलें।",
    "ta": "இது ஒரு AI திரையிடல் கருவி, மருத்துவ நோயறிதல் அல்ல. தயவுசெய்து ஒரு தகுதிவாய்ந்த மருத்துவரை அணுகவும்.",
    "te": "ఇది ఒక AI స్క్రీనింగ్ సాధనం, వైద్య నిర్ధారణ కాదు. దయచేసి అర్హత గల వైద్యుడిని సంప్రదించండి.",
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _extract_json(text: str) -> dict:
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    raise ValueError(f"No JSON in Gemini response: {text!r}")


def _format_symptoms(symptoms: dict | None, scan_type: str) -> str:
    if not symptoms:
        return "  No symptom information provided."
    lines = []
    for question, answer in symptoms.items():
        if question and answer:
            lines.append(f"  - {question}: {answer}")
    return "\n".join(lines) if lines else "  No symptom information provided."


# ── Public API ─────────────────────────────────────────────────────────────────

async def check_image_quality(image_bytes: bytes) -> dict:
    """Returns {"quality": "GOOD"} or {"quality": "BAD", "reason": "..."}."""
    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
    try:
        response = await _client.aio.models.generate_content(
            model=_MODEL,
            contents=[_QUALITY_PROMPT, image_part],
        )
        try:
            result = _extract_json(response.text)
            return result
        except Exception:
            text = response.text.strip().upper()
            if "BAD" in text:
                reason = response.text.split(":", 1)[-1].strip()[:120]
                return {"quality": "BAD", "reason": reason}
            return {"quality": "GOOD", "reason": ""}
    except Exception as exc:
        logger.error("Gemini quality check error: %s — failing open", exc)
        return {"quality": "GOOD", "reason": ""}


async def analyze_image_with_gemini(
    image_bytes: bytes,
    risk_level: str,
    confidence: float,
    scan_type: str = "oral",
    symptoms: dict | None = None,
) -> dict:
    """Returns dict with keys: en, hi, ta, te, action_required."""
    symptoms_text = _format_symptoms(symptoms, scan_type)
    prompt = _ANALYSIS_PROMPT.format(
        scan_type=scan_type,
        risk_level=risk_level,
        confidence=round(confidence * 100),
        symptoms_text=symptoms_text,
    )
    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

    try:
        response = await _client.aio.models.generate_content(
            model=_MODEL,
            contents=[prompt, image_part],
        )
        result = _extract_json(response.text)
        # Validate required keys
        for lang in ("en", "hi", "ta", "te"):
            if lang not in result or not result[lang]:
                result[lang] = _FALLBACK[lang]
        if "action_required" not in result:
            result["action_required"] = risk_level == "HIGH_RISK"
        if "concern" not in result or not result["concern"]:
            result["concern"] = (
                "Please visit a doctor soon." if risk_level == "HIGH_RISK"
                else "Monitor the area and see a doctor if anything changes."
            )
        logger.info("Gemini analysis: scan=%s risk=%s concern=%s",
                    scan_type, risk_level, result["concern"][:60])
        return result
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning("Gemini JSON parse failed (%s) — using fallback", exc)
        return _FALLBACK.copy()
    except Exception as exc:
        logger.error("Gemini API error: %s", exc)
        return _ERROR.copy()


async def generate_questions_for_image(
    image_bytes: bytes,
    scan_type: str = "oral",
) -> list[dict]:
    """Use Gemini vision to generate contextual symptom questions from the image.
    Returns list of question dicts with id, en/hi/ta/te text, and options."""
    prompt = _QUESTIONS_PROMPT.format(scan_type=scan_type)
    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

    try:
        response = await _client.aio.models.generate_content(
            model=_MODEL,
            contents=[prompt, image_part],
        )
        data = _extract_json(response.text)
        questions = data.get("questions", [])
        if questions and len(questions) >= 2:
            logger.info("Gemini generated %d questions for %s scan", len(questions), scan_type)
            return questions
    except Exception as exc:
        logger.warning("Gemini question generation failed (%s) — using static fallback", exc)

    # Fallback to static questions if Gemini fails
    return SYMPTOM_QUESTIONS.get(scan_type, SYMPTOM_QUESTIONS["oral"])


_PDF_NARRATIVE_PROMPT = """\
You are a compassionate medical AI writing a personalised health screening report for a rural Indian patient.
The report must be clear, warm, and never use frightening medical jargon.

PATIENT DATA:
- Scan type: {scan_type}
- AI risk result: {risk_level} (confidence {confidence}%)
- Patient symptoms:
{symptoms_text}
- Gemini visual finding: {gemini_finding}

TASK: Generate a detailed, personalised narrative for this specific patient's PDF report.
Every field must feel personal — mention their specific symptoms and what the AI actually saw.

Respond ONLY in this exact JSON (no markdown):
{{
    "summary_en": "3-4 sentences. Start 'Your screening result shows...'. Describe what the AI found in this specific scan, connect it naturally to the symptoms the patient reported. Mention the confidence level naturally. End with one calm, clear action step. No medical jargon.",
    "summary_hi": "3-4 वाक्य। शुरुआत 'आपकी जांच का परिणाम...' से। उनके लक्षणों का जिक्र करें। सरल भाषा।",
    "summary_ta": "3-4 வாக்கியங்கள். 'உங்கள் பரிசோதனை முடிவு...' என தொடங்கவும். அவர்களின் அறிகுறிகளை இயற்கையாக குறிப்பிடவும்.",
    "summary_te": "3-4 వాక్యాలు. 'మీ స్క్రీనింగ్ ఫలితం...' తో ప్రారంభించండి. వారి లక్షణాలను సహజంగా పేర్కొనండి.",
    "next_steps": [
        "Step 1 in plain English — specific and actionable (e.g., 'Visit your nearest PHC or community health centre within the next 2 days')",
        "Step 2 — something they can do at home (e.g., 'Take clear photos of the area every 3 days to track any changes')",
        "Step 3 — general health advice relevant to this scan type"
    ],
    "tell_doctor": [
        "Key point 1 to tell the doctor — based on the specific symptoms reported",
        "Key point 2 — duration and progression details",
        "Key point 3 — any lifestyle factor relevant to this scan type (tobacco, sun, diet)"
    ],
    "lifestyle_tip": "One specific, practical lifestyle tip for this patient based on their scan type and symptoms. For oral: mention tobacco, betel nut, diet. For skin: mention sun protection, moisturising. Keep it warm and non-judgmental.",
    "urgency": "URGENT" | "SOON" | "ROUTINE"
}}

Rules:
- urgency: URGENT if HIGH_RISK, SOON if HIGH_RISK with short duration, ROUTINE if LOW_RISK
- HIGH_RISK: next_steps[0] must say visit doctor within 2 days
- LOW_RISK: next_steps can say monthly self-check
- NEVER say: cancer, tumor, malignant, lesion, carcinoma, biopsy, oncology
- Use: area, spot, patch, mark, change, finding, concern
- Make tell_doctor specific to the symptoms actually reported, not generic
"""

async def generate_pdf_narrative(
    scan_type: str,
    risk_level: str,
    confidence: float,
    symptoms: dict | None,
    gemini_finding: str,
) -> dict:
    """Generate rich, personalised narrative for the PDF report using Gemini.
    Returns dict with summary_en/hi/ta/te, next_steps, tell_doctor, lifestyle_tip, urgency."""
    symptoms_text = _format_symptoms(symptoms, scan_type)
    prompt = _PDF_NARRATIVE_PROMPT.format(
        scan_type=scan_type,
        risk_level=risk_level,
        confidence=round(confidence * 100),
        symptoms_text=symptoms_text,
        gemini_finding=gemini_finding[:300] if gemini_finding else "Not available",
    )
    try:
        response = await _client.aio.models.generate_content(
            model=_MODEL,
            contents=[prompt],
        )
        result = _extract_json(response.text)
        # Ensure required fields
        if "next_steps" not in result or not result["next_steps"]:
            result["next_steps"] = [
                "Visit your nearest health centre as soon as possible.",
                "Show this report to the doctor along with the photo.",
                "Do not use any home remedies on the affected area.",
            ]
        if "tell_doctor" not in result or not result["tell_doctor"]:
            result["tell_doctor"] = [
                "How long you have had this problem.",
                "Any pain or discomfort you feel.",
                "Any changes you have noticed over time.",
            ]
        if "urgency" not in result:
            result["urgency"] = "URGENT" if risk_level == "HIGH_RISK" else "ROUTINE"
        if "lifestyle_tip" not in result:
            result["lifestyle_tip"] = (
                "Avoid tobacco and betel nut products, and maintain good oral hygiene."
                if scan_type == "oral"
                else "Apply sunscreen daily and wear protective clothing when outdoors."
            )
        logger.info("PDF narrative generated: scan=%s risk=%s urgency=%s",
                    scan_type, risk_level, result.get("urgency"))
        return result
    except Exception as exc:
        logger.error("PDF narrative generation failed: %s", exc)
        return {
            "summary_en": (
                "Your screening result shows some areas that need attention. "
                "The AI model has analysed your image. Please visit a doctor for a proper evaluation."
            ),
            "summary_hi": "आपकी जांच के परिणाम में कुछ बातें ध्यान देने योग्य हैं। कृपया डॉक्टर से मिलें।",
            "summary_ta": "உங்கள் பரிசோதனை முடிவு சில பகுதிகளில் கவனிக்க வேண்டியவை உள்ளன. மருத்துவரை அணுகவும்.",
            "summary_te": "మీ స్క్రీనింగ్ ఫలితం కొన్ని ప్రాంతాలలో శ్రద్ధ అవసరమని చూపిస్తోంది. వైద్యుడిని సంప్రదించండి.",
            "next_steps": [
                "Visit your nearest health centre as soon as possible.",
                "Bring this report and your phone to show the photo to the doctor.",
                "Do not apply any home remedies to the affected area.",
            ],
            "tell_doctor": [
                "How long you have had this problem.",
                "Whether there is any pain, burning, or itching.",
                "Whether it has changed in size or colour.",
            ],
            "lifestyle_tip": (
                "Avoid tobacco and betel nut products and maintain good oral hygiene."
                if scan_type == "oral"
                else "Apply sunscreen daily and protect your skin from excessive sun exposure."
            ),
            "urgency": "URGENT" if risk_level == "HIGH_RISK" else "ROUTINE",
        }


async def chat_health(
    message: str,
    history: list[dict],
    language: str = "en",
) -> dict:
    """General health chat using Gemini. Returns {response, error}.
    history: list of {role: 'user'|'assistant', content: str}
    """
    lang_names = {"en": "English", "hi": "Hindi", "ta": "Tamil", "te": "Telugu"}
    lang_name  = lang_names.get(language, "English")
    system     = _CHAT_SYSTEM.format(language=lang_name)

    # Build properly structured Contents for the google-genai SDK.
    # Roles must be "user" or "model" (not "assistant").
    contents: list[types.Content] = []
    for turn in history[-10:]:
        role    = turn.get("role", "user")
        content = turn.get("content", "")
        if not content:
            continue
        gemini_role = "user" if role == "user" else "model"
        contents.append(
            types.Content(role=gemini_role, parts=[types.Part(text=content)])
        )
    contents.append(
        types.Content(role="user", parts=[types.Part(text=message)])
    )

    try:
        response = await _client.aio.models.generate_content(
            model=_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system,
            ),
        )
        reply = response.text.strip()
        logger.info("Health chat: lang=%s tokens~=%d", language, len(reply.split()))
        return {"response": reply, "error": None}
    except Exception as exc:
        logger.error("Health chat error: %s", exc)
        fallback = {
            "en": "I'm having trouble responding right now. Please try again.",
            "hi": "मुझे अभी जवाब देने में परेशानी हो रही है। कृपया दोबारा कोशिश करें।",
            "ta": "எனக்கு இப்போது பதிலளிக்க சிக்கல் உள்ளது. மீண்டும் முயற்சிக்கவும்.",
            "te": "నాకు ఇప్పుడు సమాధానం ఇవ్వడంలో సమస్య ఉంది. దయచేసి మళ్ళీ ప్రయత్నించండి.",
        }
        return {"response": fallback.get(language, fallback["en"]), "error": str(exc)}
