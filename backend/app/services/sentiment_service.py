import joblib

from app.config import MODELS_DIR
from app.services import llm_service

_vectorizer = None
_clf = None


def _load():
    global _vectorizer, _clf
    if _vectorizer is None:
        _vectorizer = joblib.load(MODELS_DIR / "sentiment_tfidf_vectorizer.joblib")
        _clf = joblib.load(MODELS_DIR / "sentiment_clf.joblib")
    return _vectorizer, _clf


def classify_baseline(text: str) -> dict:
    vectorizer, clf = _load()
    vec = vectorizer.transform([text])
    tone = clf.predict(vec)[0]
    proba = clf.predict_proba(vec)[0]
    confidence = float(max(proba))
    return {"tone": tone, "confidence": round(confidence, 4)}


def analyze(text: str, use_llm: bool = True) -> dict:
    baseline = classify_baseline(text)
    result = {"baseline": baseline, "llm": None}
    if use_llm and llm_service.is_available():
        llm_result = llm_service.analyze_sentiment_llm(text)
        if llm_result and "error" not in llm_result:
            result["llm"] = llm_result
    return result
