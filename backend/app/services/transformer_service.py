"""
Inference wrapper for the fine-tuned multilingual DistilBERT crime-type
classifier (see app/ml/train_transformer.py). Used alongside the TF-IDF
baseline (classification_service) so the NLP endpoint and the evaluation
framework can report both.
"""
import json

from app.config import MODELS_DIR

_tokenizer = None
_model = None
_label_map = None

TRANSFORMER_DIR = MODELS_DIR / "transformer"


def is_available() -> bool:
    return (TRANSFORMER_DIR / "config.json").exists()


def _load():
    global _tokenizer, _model, _label_map
    if _model is None:
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        _tokenizer = AutoTokenizer.from_pretrained(TRANSFORMER_DIR)
        _model = AutoModelForSequenceClassification.from_pretrained(TRANSFORMER_DIR)
        _model.eval()
        _label_map = {int(k): v for k, v in json.loads((TRANSFORMER_DIR / "label_map.json").read_text(encoding="utf-8")).items()}
    return _tokenizer, _model, _label_map


def classify(text: str) -> dict:
    import torch

    tokenizer, model, label_map = _load()
    inputs = tokenizer(text, truncation=True, padding=True, max_length=96, return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits
        probs = torch.softmax(logits, dim=-1)[0]
    pred_idx = int(torch.argmax(probs).item())
    return {
        "crime_type": label_map[pred_idx],
        "confidence": round(float(probs[pred_idx]), 4),
    }
