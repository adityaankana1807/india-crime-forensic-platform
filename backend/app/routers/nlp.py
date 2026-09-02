from fastapi import APIRouter

from app.schemas import NlpAnalyzeRequest, NlpAnalyzeResponse
from app.services import classification_service, forensic_service, language_service, transformer_service

router = APIRouter(prefix="/api/nlp", tags=["nlp"])


@router.post("/analyze", response_model=NlpAnalyzeResponse)
def analyze(payload: NlpAnalyzeRequest):
    lang_code, lang_name, lang_conf = language_service.detect_language(payload.text)

    translated = None
    if payload.translate_to:
        translated = language_service.translate_text(payload.text, payload.translate_to)

    clf = classification_service.classify(payload.text)
    keyword_flags = forensic_service.find_risk_keywords(payload.text)

    transformer_crime_type = None
    transformer_confidence = None
    if transformer_service.is_available():
        t_result = transformer_service.classify(payload.text)
        transformer_crime_type = t_result["crime_type"]
        transformer_confidence = t_result["confidence"]

    return NlpAnalyzeResponse(
        text=payload.text,
        detected_language=lang_code,
        detected_language_name=lang_name,
        language_confidence=round(lang_conf, 4),
        translated_text=translated,
        crime_type=clf["crime_type"],
        threat_level=clf["threat_level"],
        threat_level_confidence=clf["threat_level_confidence"],
        keyword_flags=keyword_flags,
        transformer_crime_type=transformer_crime_type,
        transformer_confidence=transformer_confidence,
    )
