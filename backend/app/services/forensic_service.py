import hashlib
import re

RE_EMAIL = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
RE_IP = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
RE_PHONE = re.compile(r"\+?\d[\d\s().-]{7,}\d")
RE_URL = re.compile(r"https?://[^\s]+")
RE_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b")

# Multilingual risk/threat keyword list (weapons, violence, trafficking terms)
# covering India's major languages: English, Hindi, Bengali, Marathi, Tamil, Telugu.
RISK_KEYWORDS = {
    "en": ["knife", "gun", "pistol", "weapon", "kill", "bomb", "explosive", "hostage", "drugs", "traffick", "extortion", "kidnap"],
    "hi": ["चाकू", "बंदूक", "कट्टा", "हथियार", "मारना", "बम", "विस्फोटक", "बंधक", "नशीली दवा", "तस्करी", "अपहरण", "फिरौती"],
    "bn": ["ছুরি", "বন্দুক", "পিস্তল", "অস্ত্র", "হত্যা", "বোমা", "বিস্ফোরক", "জিম্মি", "মাদক", "পাচার", "অপহরণ", "মুক্তিপণ"],
    "mr": ["चाकू", "बंदूक", "कट्टा", "शस्त्र", "खून", "बॉम्ब", "स्फोटक", "ओलीस", "अंमली पदार्थ", "तस्करी", "अपहरण", "खंडणी"],
    "ta": ["கத்தி", "துப்பாக்கி", "ஆயுதம்", "கொலை", "குண்டு", "வெடிபொருள்", "பணயக்கைதி", "போதைப்பொருள்", "கடத்தல்", "மீட்கும் தொகை"],
    "te": ["కత్తి", "తుపాకీ", "ఆయుధం", "హత్య", "బాంబు", "పేలుడు పదార్థం", "బందీ", "మాదక ద్రవ్యాలు", "అక్రమ రవాణా", "అపహరణ", "విమోచన"],
}

ALL_KEYWORDS = sorted({kw.lower() for kws in RISK_KEYWORDS.values() for kw in kws})


def sha256_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_entities(text: str) -> dict:
    dates = sorted(set(RE_DATE.findall(text)))
    phones = sorted(set(RE_PHONE.findall(text)) - set(dates))
    return {
        "emails": sorted(set(RE_EMAIL.findall(text))),
        "ip_addresses": sorted(set(RE_IP.findall(text))),
        "phone_numbers": phones,
        "urls": sorted(set(RE_URL.findall(text))),
        "dates": dates,
    }


def find_risk_keywords(text: str) -> list[str]:
    lowered = text.lower()
    return sorted({kw for kw in ALL_KEYWORDS if kw in lowered})


def score_risk(keyword_flags: list[str], entities: dict) -> tuple[int, str]:
    score = len(keyword_flags) * 20
    score += 10 if entities["ip_addresses"] else 0
    score += 5 if entities["emails"] else 0
    score = min(score, 100)
    if score >= 60:
        level = "critical"
    elif score >= 35:
        level = "high"
    elif score >= 15:
        level = "medium"
    else:
        level = "low"
    return score, level
