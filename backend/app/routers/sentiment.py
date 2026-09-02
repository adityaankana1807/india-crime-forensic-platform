from fastapi import APIRouter

from app.schemas import SentimentAnalyzeRequest
from app.services import llm_service, sentiment_service

router = APIRouter(prefix="/api/sentiment", tags=["sentiment"])


@router.post("/analyze")
def analyze(payload: SentimentAnalyzeRequest):
    return sentiment_service.analyze(payload.text, use_llm=payload.use_llm)


@router.get("/llm-status")
def llm_status():
    return {"llm_available": llm_service.is_available()}
