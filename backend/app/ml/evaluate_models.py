"""
Evaluation framework for the paper's Results section: compares the TF-IDF
baseline, fine-tuned transformer, and (if ANTHROPIC_API_KEY is set) Claude
zero-shot classification on the same held-out crime-type test split, with a
per-language breakdown and confusion matrices.

The LLM comparison samples a subset of the test set (default 60 examples) to
keep API cost/time bounded — increase LLM_SAMPLE_SIZE for a larger run.

Run: python evaluate_models.py
"""
import json
import sys
import time
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

DATA_PATH = ROOT / "data" / "synthetic" / "crime_reports_multilingual.csv"
MODELS_DIR = Path(__file__).resolve().parent / "models"
TRANSFORMER_DIR = MODELS_DIR / "transformer"
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)

LLM_SAMPLE_SIZE = 60


def load_test_split():
    df = pd.read_csv(DATA_PATH).dropna(subset=["text", "crime_type", "language"])
    _, test_df = train_test_split(
        df, test_size=0.2, random_state=42, stratify=df["crime_type"],
    )
    return test_df.reset_index(drop=True)


def eval_baseline(test_df):
    vectorizer = joblib.load(MODELS_DIR / "tfidf_vectorizer.joblib")
    clf = joblib.load(MODELS_DIR / "crime_type_clf.joblib")
    X = vectorizer.transform(test_df["text"])
    preds = clf.predict(X)
    return preds


def eval_transformer(test_df):
    if not (TRANSFORMER_DIR / "config.json").exists():
        return None
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(TRANSFORMER_DIR)
    model = AutoModelForSequenceClassification.from_pretrained(TRANSFORMER_DIR)
    model.eval()
    label_map = {int(k): v for k, v in json.loads((TRANSFORMER_DIR / "label_map.json").read_text(encoding="utf-8")).items()}

    preds = []
    with torch.no_grad():
        for text in test_df["text"]:
            inputs = tokenizer(text, truncation=True, padding=True, max_length=96, return_tensors="pt")
            logits = model(**inputs).logits
            pred_idx = int(torch.argmax(logits, dim=-1).item())
            preds.append(label_map[pred_idx])
    return np.array(preds)


def eval_llm_zero_shot(test_df, crime_types):
    from app.services import llm_service
    if not llm_service.is_available():
        return None, None

    sample = test_df.sample(n=min(LLM_SAMPLE_SIZE, len(test_df)), random_state=42)
    preds = []
    types_str = ", ".join(crime_types)
    for text in sample["text"]:
        prompt = (
            f"Classify the crime type described in this text (which may be in "
            f"English, Hindi, Bengali, Marathi, Tamil, or Telugu) into exactly "
            f"one of these categories: {types_str}.\n\nText: \"{text}\"\n\n"
            f"Respond with ONLY the category name, nothing else."
        )
        client = llm_service._get_client()
        try:
            resp = client.messages.create(
                model=llm_service.MODEL, max_tokens=20,
                messages=[{"role": "user", "content": prompt}],
            )
            pred = resp.content[0].text.strip().lower()
            pred = pred if pred in crime_types else "unknown"
        except Exception:
            pred = "unknown"
        preds.append(pred)
        time.sleep(0.2)  # gentle rate limiting
    return sample, np.array(preds)


def per_language_breakdown(test_df, preds):
    out = {}
    for lang in sorted(test_df["language"].unique()):
        mask = (test_df["language"] == lang).to_numpy()
        out[lang] = {
            "accuracy": round(float(accuracy_score(test_df["crime_type"][mask], preds[mask])), 4),
            "macro_f1": round(float(f1_score(test_df["crime_type"][mask], preds[mask], average="macro")), 4),
            "n": int(mask.sum()),
        }
    return out


def save_confusion_matrix(y_true, y_pred, labels, title, filename):
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    fig, ax = plt.subplots(figsize=(9, 8))
    ConfusionMatrixDisplay(cm, display_labels=labels).plot(ax=ax, xticks_rotation=45, colorbar=False)
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / filename, dpi=150)
    plt.close(fig)


def main():
    test_df = load_test_split()
    crime_types = sorted(test_df["crime_type"].unique().tolist())
    y_true = test_df["crime_type"]

    comparison = {}

    baseline_preds = eval_baseline(test_df)
    comparison["tfidf_svm_baseline"] = {
        "accuracy": round(float(accuracy_score(y_true, baseline_preds)), 4),
        "macro_f1": round(float(f1_score(y_true, baseline_preds, average="macro")), 4),
        "per_language": per_language_breakdown(test_df, baseline_preds),
    }
    save_confusion_matrix(y_true, baseline_preds, crime_types, "TF-IDF + LinearSVC — Confusion Matrix", "confusion_matrix_baseline.png")

    transformer_preds = eval_transformer(test_df)
    if transformer_preds is not None:
        comparison["distilbert_multilingual"] = {
            "accuracy": round(float(accuracy_score(y_true, transformer_preds)), 4),
            "macro_f1": round(float(f1_score(y_true, transformer_preds, average="macro")), 4),
            "per_language": per_language_breakdown(test_df, transformer_preds),
        }
        save_confusion_matrix(y_true, transformer_preds, crime_types, "Fine-tuned Multilingual DistilBERT — Confusion Matrix", "confusion_matrix_transformer.png")
    else:
        comparison["distilbert_multilingual"] = {"status": "not trained — run train_transformer.py first"}

    llm_sample, llm_preds = eval_llm_zero_shot(test_df, crime_types)
    if llm_preds is not None:
        comparison["claude_zero_shot"] = {
            "accuracy": round(float(accuracy_score(llm_sample["crime_type"], llm_preds)), 4),
            "macro_f1": round(float(f1_score(llm_sample["crime_type"], llm_preds, average="macro", labels=crime_types)), 4),
            "per_language": per_language_breakdown(llm_sample, llm_preds),
            "sample_size": len(llm_sample),
        }
        save_confusion_matrix(llm_sample["crime_type"], llm_preds, crime_types, "Claude Zero-Shot — Confusion Matrix", "confusion_matrix_llm.png")
    else:
        comparison["claude_zero_shot"] = {"status": "skipped — ANTHROPIC_API_KEY not set"}

    (RESULTS_DIR / "model_comparison.json").write_text(json.dumps(comparison, indent=2, ensure_ascii=False))
    print(json.dumps(comparison, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
