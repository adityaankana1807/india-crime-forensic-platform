import joblib

from app.config import MODELS_DIR

_vectorizer = None
_crime_clf = None
_threat_clf = None


def _load():
    global _vectorizer, _crime_clf, _threat_clf
    if _vectorizer is None:
        _vectorizer = joblib.load(MODELS_DIR / "tfidf_vectorizer.joblib")
        _crime_clf = joblib.load(MODELS_DIR / "crime_type_clf.joblib")
        _threat_clf = joblib.load(MODELS_DIR / "threat_clf.joblib")
    return _vectorizer, _crime_clf, _threat_clf


def classify(text: str) -> dict:
    vectorizer, crime_clf, threat_clf = _load()
    vec = vectorizer.transform([text])

    crime_type = crime_clf.predict(vec)[0]

    threat_level = threat_clf.predict(vec)[0]
    proba = threat_clf.predict_proba(vec)[0]
    threat_confidence = float(max(proba))

    return {
        "crime_type": crime_type,
        "threat_level": threat_level,
        "threat_level_confidence": round(threat_confidence, 4),
    }
