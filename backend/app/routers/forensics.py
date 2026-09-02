from fastapi import APIRouter

from app.schemas import ForensicAnalyzeRequest, ForensicAnalyzeResponse
from app.services import forensic_service, language_service, llm_service

router = APIRouter(prefix="/api/forensics", tags=["forensics"])


@router.post("/analyze", response_model=ForensicAnalyzeResponse)
def analyze(payload: ForensicAnalyzeRequest):
    lang_code, _, _ = language_service.detect_language(payload.text)
    entities = forensic_service.extract_entities(payload.text)
    keywords = forensic_service.find_risk_keywords(payload.text)
    score, level = forensic_service.score_risk(keywords, entities)

    llm_extraction = None
    if payload.use_llm and llm_service.is_available():
        result = llm_service.extract_entities_llm(payload.text)
        if result and "error" not in result:
            llm_extraction = result

    return ForensicAnalyzeResponse(
        sha256=forensic_service.sha256_hash(payload.text),
        detected_language=lang_code,
        entities=entities,
        risk_keywords=keywords,
        risk_score=score,
        risk_level=level,
        llm_extraction=llm_extraction,
    )
