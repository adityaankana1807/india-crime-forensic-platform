"""
Fine-tunes a multilingual transformer (DistilBERT-multilingual by default) on
the crime-type classification task, as a comparison point against the TF-IDF
+ LinearSVC baseline in train_models.py for the paper's model-comparison /
Results section.

DistilBERT-multilingual (~135M params, 104 languages) is used instead of the
larger XLM-RoBERTa-base (~270M) to keep CPU fine-tuning time reasonable; swap
MODEL_NAME below to "xlm-roberta-base" if a GPU is available.

Run: python train_transformer.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from torch.utils.data import Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)

MODEL_NAME = "distilbert-base-multilingual-cased"
ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = ROOT / "data" / "synthetic" / "crime_reports_multilingual.csv"
MODELS_DIR = Path(__file__).resolve().parent / "models" / "transformer"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


class TextDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: v[idx] for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy_score(labels, preds),
        "macro_f1": f1_score(labels, preds, average="macro"),
    }


def train():
    df = pd.read_csv(DATA_PATH).dropna(subset=["text", "crime_type", "language"])

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df["crime_type"])

    X_train, X_test, y_train, y_test, lang_train, lang_test = train_test_split(
        df["text"].tolist(), y, df["language"].tolist(),
        test_size=0.2, random_state=42, stratify=y,
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    train_enc = tokenizer(X_train, truncation=True, padding=True, max_length=96, return_tensors="pt")
    test_enc = tokenizer(X_test, truncation=True, padding=True, max_length=96, return_tensors="pt")

    train_ds = TextDataset(train_enc, y_train)
    test_ds = TextDataset(test_enc, y_test)

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME, num_labels=len(label_encoder.classes_),
    )

    args = TrainingArguments(
        output_dir=str(MODELS_DIR / "checkpoints"),
        num_train_epochs=4,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=16,
        eval_strategy="epoch",
        save_strategy="no",
        logging_steps=20,
        learning_rate=3e-5,
        report_to=[],
    )

    trainer = Trainer(
        model=model, args=args,
        train_dataset=train_ds, eval_dataset=test_ds,
        compute_metrics=compute_metrics,
    )
    trainer.train()
    overall_metrics = trainer.evaluate()

    # Per-language breakdown — important for a *multilingual* paper's Results section.
    logits = trainer.predict(test_ds).predictions
    preds = np.argmax(logits, axis=-1)
    per_language = {}
    lang_arr = np.array(lang_test)
    for lang in sorted(set(lang_test)):
        mask = lang_arr == lang
        per_language[lang] = {
            "accuracy": round(float(accuracy_score(np.array(y_test)[mask], preds[mask])), 4),
            "macro_f1": round(float(f1_score(np.array(y_test)[mask], preds[mask], average="macro")), 4),
            "n": int(mask.sum()),
        }

    model.save_pretrained(MODELS_DIR)
    tokenizer.save_pretrained(MODELS_DIR)
    joblib_labels = {int(i): label for i, label in enumerate(label_encoder.classes_)}
    (MODELS_DIR / "label_map.json").write_text(json.dumps(joblib_labels, indent=2, ensure_ascii=False))

    metrics = {
        "model_name": MODEL_NAME,
        "overall_accuracy": round(overall_metrics["eval_accuracy"], 4),
        "overall_macro_f1": round(overall_metrics["eval_macro_f1"], 4),
        "per_language": per_language,
        "train_size": len(X_train),
        "test_size": len(X_test),
    }
    (RESULTS_DIR / "transformer_metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False))
    print("Transformer training complete:", json.dumps(metrics, indent=2, ensure_ascii=False))
    return metrics


if __name__ == "__main__":
    train()
