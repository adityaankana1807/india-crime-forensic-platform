from langdetect import DetectorFactory, detect_langs

from app.config import SUPPORTED_LANGUAGES

DetectorFactory.seed = 42  # deterministic detection


def detect_language(text: str) -> tuple[str, str, float]:
    try:
        candidates = detect_langs(text)
        top = candidates[0]
        code = top.lang
        confidence = float(top.prob)
    except Exception:
        code, confidence = "unknown", 0.0
    name = SUPPORTED_LANGUAGES.get(code, code)
    return code, name, confidence


def translate_text(text: str, target: str = "en") -> str | None:
    try:
        from deep_translator import GoogleTranslator
        result = GoogleTranslator(source="auto", target=target).translate(text)
        if not result or "<html" in result.lower() or "That's an error" in result:
            return None  # upstream returned an error page instead of raising
        return result
    except Exception:
        # No internet access / translation service unreachable — degrade gracefully.
        return None
