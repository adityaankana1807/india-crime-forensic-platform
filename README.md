# India Crime Behaviour & Digital-Forensic Evidence Analysis Platform

> **Paper-facing console (2026):** the interactive research product — official NCRB metro tables, 32-agency register, paraphrastic Indic corpus, hybrid NLP/DFIR, Grok grounded analysis, and a 10-gap literature register — is **[NyayaLens](https://github.com/adityaankana1807/nyayalens)**.
>
> This repository remains the **Python ML lab**: FastAPI, TF-IDF/SVM, DistilBERT, NCRB XLSX/CSV, and the honest finding that template synthetics yield ~99% accuracy and are *not* a benchmark.

An AI-driven, multilingual platform for analysing **criminal behaviour patterns**,
**sentiment/emotional-tone**, and **digital-forensic evidence** in the Indian
context. Built on real NCRB (National Crime Records Bureau) statistics plus
synthetic, India-focused multilingual datasets (English, Hindi, Bengali,
Marathi, Tamil, Telugu).

## What it does

- **Criminal behaviour analysis** (core focus) — links synthetic crime reports
  into repeat-offender incident sequences (`suspect_id`/`mo_cluster`) and
  computes modus-operandi consistency, escalation trend, and geographic
  spread per suspect; an LLM generates a qualitative behavioural
  narrative from the structured incident history.
- **Sentiment / emotional-tone analysis** (core focus) — classifies evidence
  text (chat logs, messages) into deceptive / threatening / neutral /
  distressed, via a trained TF-IDF baseline cross-checked against an LLM.
- **Multilingual NLP analysis** — detects language, classifies crime type and
  threat level via **two independent models** (TF-IDF+SVM baseline and a
  fine-tuned multilingual DistilBERT transformer, so results can be compared
  side by side), and translates text.
- **Digital-forensic evidence analysis** — extracts entities (emails, IPs,
  phone numbers, URLs, dates) via regex, extracts richer structured entities
  (persons, organisations, offence indicators) via an LLM, flags multilingual
  risk/threat keywords, computes a SHA-256 integrity hash, and scores risk.
- **Crime hotspot analysis** — DBSCAN geospatial clustering and temporal trend
  analysis over crime records.
- **Dataset browser** — browse, preview, and upload CSV datasets.

## NLP / LLM methodology (for the paper's Results section)

Three approaches are compared on the same held-out crime-type classification
test split (`backend/app/ml/evaluate_models.py`):

| Model | Description |
|---|---|
| TF-IDF + LinearSVC | Character n-gram baseline, `train_models.py` |
| DistilBERT-multilingual (fine-tuned) | Transformer, `train_transformer.py` |
| LLM zero-shot | No fine-tuning, prompted classification |

Results land in `backend/results/`: `model_comparison.json`,
`baseline_metrics.json`, `transformer_metrics.json`, `sentiment_metrics.json`,
and confusion-matrix PNGs per model, each with a **per-language breakdown**
(important for a multilingual paper's Results section).

**Honest limitation to report in the paper**: both the TF-IDF baseline and
the fine-tuned transformer reach ~99-100% accuracy on the current synthetic
crime-report dataset. This is expected — the dataset is generated from a
fixed set of per-crime-type sentence templates (see
`generate_synthetic_datasets.py`), so the categories are lexically very
separable and the task is close to trivial for both models. This makes the
dataset good for demonstrating a working end-to-end multilingual pipeline,
but **not** a meaningful benchmark for comparing model capability — a fairer
comparison needs either (a) real, human-written crime-report text (harder to
obtain for India due to privacy/availability), or (b) a harder synthetic set
with paraphrastic variation/noise injected per example (see NyayaLens).

## Data

- `backend/data/raw/` — **real data**:
  - `ncrb_ipc_crimes_citywise_2023.csv`, `ncrb_crimes_against_women_citywise_2023.csv`,
    `ncrb_cyber_crimes_disposal_citywise_2023.csv`, `ncrb_ndps_seizures_citywise_2023.csv`,
    `ncrb_property_stolen_recovered_citywise_2023.csv` — NCRB "Crime in India 2023"
    city-wise statistics across 53 Indian metropolitan cities, sourced via the
    Open Government Data Platform India mirror (data.opencity.in). Original
    XLSX source files are kept under `ncrb_xlsx/`.
  - `indian_law_enforcement_agencies.csv` — curated reference dataset of Indian
    crime-investigation, intelligence, financial-crime, narcotics, forensic-science
    and paramilitary agencies (CBI, NIA, NCRB, ED, NCB, DRI, SFIO, IB, CFSL, etc.)
  - `chicago_crime.csv`, `communities_crime.csv` — real public datasets (Chicago
    open data portal, UCI ML repository) kept for cross-country comparison.
- `backend/data/synthetic/` — **synthetic, India-themed**:
  - `crime_reports_multilingual.csv` — labeled crime-report narratives
    across IPC/NCRB-aligned crime categories in multiple languages.
  - `forensic_evidence_logs.csv` — synthetic chat/email/SMS evidence
    snippets labeled with emotional tone.
  - `crime_hotspots.csv` — synthetic geotagged records around major Indian metros.

## Architecture

- **ML lab (this repo)**: FastAPI + scikit-learn + pandas + transformers/torch
- **Paper console**: [NyayaLens](https://github.com/adityaankana1807/nyayalens)
