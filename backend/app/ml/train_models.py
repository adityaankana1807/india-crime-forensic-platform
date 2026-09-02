"""
Trains the platform's ML models on the multilingual synthetic crime-report
dataset:
  - crime_type_clf: TF-IDF + LinearSVC, predicts crime category from text
  - threat_clf: TF-IDF + LogisticRegression, predicts threat level from text

Run: python train_models.py
"""
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = ROOT / "data" / "synthetic" / "crime_reports_multilingual.csv"
MODELS_DIR = Path(__file__).resolve().parent / "models"
MODELS_DIR.mkdir(exist_ok=True)
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def train():
    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=["text", "crime_type", "threat_level"])

    X_train, X_test, y_type_train, y_type_test, y_threat_train, y_threat_test = train_test_split(
        df["text"], df["crime_type"], df["threat_level"],
        test_size=0.2, random_state=42, stratify=df["crime_type"],
    )

    vectorizer = TfidfVectorizer(
        max_features=20000,
        ngram_range=(1, 2),
        analyzer="char_wb",  # character n-grams: language-agnostic, robust across scripts (Latin, Devanagari, Arabic)
    )
    Xtr = vectorizer.fit_transform(X_train)
    Xte = vectorizer.transform(X_test)

    crime_clf = LinearSVC(random_state=42)
    crime_clf.fit(Xtr, y_type_train)
    crime_pred = crime_clf.predict(Xte)
    crime_acc = accuracy_score(y_type_test, crime_pred)
    crime_f1 = f1_score(y_type_test, crime_pred, average="macro")

    threat_clf = LogisticRegression(max_iter=1000, random_state=42)
    threat_clf.fit(Xtr, y_threat_train)
    threat_pred = threat_clf.predict(Xte)
    threat_acc = accuracy_score(y_threat_test, threat_pred)
    threat_f1 = f1_score(y_threat_test, threat_pred, average="macro")

    joblib.dump(vectorizer, MODELS_DIR / "tfidf_vectorizer.joblib")
    joblib.dump(crime_clf, MODELS_DIR / "crime_type_clf.joblib")
    joblib.dump(threat_clf, MODELS_DIR / "threat_clf.joblib")

    metrics = {
        "crime_type_accuracy": round(crime_acc, 4),
        "crime_type_macro_f1": round(crime_f1, 4),
        "threat_level_accuracy": round(threat_acc, 4),
        "threat_level_macro_f1": round(threat_f1, 4),
        "train_size": len(X_train),
        "test_size": len(X_test),
    }
    print("Training complete:", metrics)
    import json
    (RESULTS_DIR / "baseline_metrics.json").write_text(json.dumps(metrics, indent=2))
    return metrics


if __name__ == "__main__":
    train()
