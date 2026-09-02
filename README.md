# India Crime Behaviour & Digital-Forensic Evidence Analysis Platform

An AI-driven, multilingual platform for analysing **criminal behaviour patterns**,
**sentiment/emotional-tone**, and **digital-forensic evidence** in the Indian
context. Built on real NCRB (National Crime Records Bureau) statistics plus
synthetic, India-focused multilingual datasets (English, Hindi, Bengali,
Marathi, Tamil, Telugu).

## What it does

- **Criminal behaviour analysis** (core focus) — links synthetic crime reports
  into repeat-offender incident sequences (`suspect_id`/`mo_cluster`) and
  computes modus-operandi consistency, escalation trend, and geographic
  spread per suspect; an LLM (Claude) generates a qualitative behavioural
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
| Claude (zero-shot) | No fine-tuning, prompted classification |

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
with paraphrastic variation/noise injected per example. The Claude zero-shot
comparison (once `ANTHROPIC_API_KEY` is set) is the more informative
comparison point since it has not seen the templates at all.

## LLM setup (Claude)

Sentiment cross-checking, LLM-based entity extraction, and behavioural
narrative generation require an Anthropic API key:
```
cd backend
cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY=sk-ant-...
```
Restart the backend after setting it. Every LLM-backed endpoint degrades
gracefully (returns `null`/`"LLM not configured"`) if the key is absent, so
the rest of the platform works without it. Check status: `GET /api/sentiment/llm-status`.

## Data

- `backend/data/raw/` — **real data**:
  - `ncrb_ipc_crimes_citywise_2023.csv`, `ncrb_crimes_against_women_citywise_2023.csv`,
    `ncrb_cyber_crimes_disposal_citywise_2023.csv`, `ncrb_ndps_seizures_citywise_2023.csv`,
    `ncrb_property_stolen_recovered_citywise_2023.csv` — NCRB "Crime in India 2023"
    city-wise statistics across 53 Indian metropolitan cities, sourced via the
    Open Government Data Platform India mirror (data.opencity.in). Original
    XLSX source files are kept under `ncrb_xlsx/`.
  - `indian_law_enforcement_agencies.csv` — curated reference dataset of 26 Indian
    crime-investigation, intelligence, financial-crime, narcotics, forensic-science
    and paramilitary agencies (CBI, NIA, NCRB, ED, NCB, DRI, SFIO, IB, CFSL, etc.)
  - `chicago_crime.csv`, `communities_crime.csv` — real public datasets (Chicago
    open data portal, UCI ML repository) kept for cross-country comparison.
- `backend/data/synthetic/` — **synthetic, India-themed, regenerated at build time**:
  - `crime_reports_multilingual.csv` — 1,200 labeled crime-report narratives
    across 12 IPC/NCRB-aligned crime categories in 6 languages. ~25% are
    linked into repeat-offender sequences (`suspect_id`, `mo_cluster`,
    `incident_index` columns) with a mild escalation trend, feeding the
    behaviour-analysis module.
  - `forensic_evidence_logs.csv` — 500 synthetic chat/email/SMS evidence
    snippets, each labeled with an `emotional_tone` (deceptive / threatening
    / neutral / distressed), feeding the sentiment-analysis module.
  - `crime_hotspots.csv` — 2,000 synthetic geotagged records clustered around
    8 major Indian metros, for hotspot-detection demos.

Regenerate synthetic data / retrain all models at any time:
```
cd backend
venv/Scripts/python data/scripts/generate_synthetic_datasets.py
venv/Scripts/python app/ml/train_models.py
venv/Scripts/python app/ml/train_sentiment_model.py
venv/Scripts/python app/ml/train_transformer.py     # ~10-15 min on CPU
venv/Scripts/python app/ml/evaluate_models.py        # writes backend/results/
```

## Architecture

- **Backend**: FastAPI + scikit-learn + pandas + transformers/torch (CPU) + Anthropic SDK (Python 3.13)
- **Frontend**: React + Vite + Recharts

## Running locally

```
# Backend
cd backend
python -m venv venv
venv/Scripts/pip install "torch>=2.6.0" --index-url https://download.pytorch.org/whl/cpu
venv/Scripts/pip install -r requirements.txt
venv/Scripts/python data/scripts/generate_synthetic_datasets.py
venv/Scripts/python app/ml/train_models.py
venv/Scripts/python app/ml/train_sentiment_model.py
venv/Scripts/python app/ml/train_transformer.py   # optional but recommended, ~10-15 min
venv/Scripts/python -m uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```
Then open http://localhost:5173.

## Running with Docker

```
docker compose up --build
```
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000

Note: the transformer is *not* fine-tuned automatically in the Docker build
(too slow for a build step) — run `train_transformer.py` locally first and
it will be picked up, or the NLP endpoint simply omits the transformer
comparison fields when the fine-tuned model isn't present.

## Tests

```
cd backend
venv/Scripts/python -m pytest tests/ -v
```
