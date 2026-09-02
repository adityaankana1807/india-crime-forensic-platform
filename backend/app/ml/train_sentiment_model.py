"""
Trains a multilingual emotional-tone (sentiment) classifier on the synthetic
forensic-evidence-log corpus: deceptive / threatening / neutral / distressed.

This is the platform's core "sentiment analysis" model — distinct from the
crime-type/threat-level classifiers in train_models.py, since it targets the
emotional register of raw evidence text (chat logs, messages) rather than
formal incident-report narratives.

Run: python train_sentiment_model.py
"""
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = ROOT / "data" / "synthetic" / "forensic_evidence_logs.csv"
MODELS_DIR = Path(__file__).resolve().parent / "models"
MODELS_DIR.mkdir(exist_ok=True)
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def train():
    df = pd.read_csv(DATA_PATH).dropna(subset=["text", "emotional_tone"])

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["emotional_tone"], test_size=0.2, random_state=42, stratify=df["emotional_tone"],
    )

    vectorizer = TfidfVectorizer(max_features=15000, ngram_range=(1, 2), analyzer="char_wb")
    Xtr = vectorizer.fit_transform(X_train)
    Xte = vectorizer.transform(X_test)

    clf = LogisticRegression(max_iter=1000, random_state=42)
    clf.fit(Xtr, y_train)
    pred = clf.predict(Xte)

    metrics = {
        "sentiment_accuracy": round(accuracy_score(y_test, pred), 4),
        "sentiment_macro_f1": round(f1_score(y_test, pred, average="macro"), 4),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "labels": sorted(df["emotional_tone"].unique().tolist()),
    }

    joblib.dump(vectorizer, MODELS_DIR / "sentiment_tfidf_vectorizer.joblib")
    joblib.dump(clf, MODELS_DIR / "sentiment_clf.joblib")
    (RESULTS_DIR / "sentiment_metrics.json").write_text(json.dumps(metrics, indent=2))

    print("Sentiment model training complete:", metrics)
    return metrics


if __name__ == "__main__":
    train()
