from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = BACKEND_ROOT / "data" / "raw"
DATA_SYNTHETIC_DIR = BACKEND_ROOT / "data" / "synthetic"
DATA_UPLOADS_DIR = BACKEND_ROOT / "data" / "uploads"
MODELS_DIR = BACKEND_ROOT / "app" / "ml" / "models"

DATA_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED_LANGUAGES = {
    "en": "English", "hi": "Hindi", "bn": "Bengali",
    "mr": "Marathi", "ta": "Tamil", "te": "Telugu",
}
