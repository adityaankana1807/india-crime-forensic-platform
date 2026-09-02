# India Crime Behaviour & Digital-Forensic Evidence Analysis Platform

An AI-driven, multilingual platform for analysing crime behaviour patterns and
digital-forensic evidence in the Indian context. Built on real NCRB (National
Crime Records Bureau) statistics plus synthetic, India-focused multilingual
datasets (English, Hindi, Bengali, Marathi, Tamil, Telugu).

## What it does

- **Multilingual NLP analysis** — detects language, classifies crime type and
  threat level (TF-IDF + ML models trained on 1,200 labeled multilingual crime
  reports), and translates text.
- **Digital-forensic evidence analysis** — extracts entities (emails, IPs,
  phone numbers, URLs, dates) from evidence text, flags multilingual
  risk/threat keywords, computes a SHA-256 integrity hash, and scores risk.
- **Crime behaviour analysis** — DBSCAN geospatial hotspot clustering and
  temporal trend analysis over crime records.
- **Dataset browser** — browse, preview, and upload CSV datasets.

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
    across 12 IPC/NCRB-aligned crime categories in 6 languages.
  - `forensic_evidence_logs.csv` — 500 synthetic chat/email/SMS evidence snippets
    with embedded entities, for forensic-extraction testing.
  - `crime_hotspots.csv` — 2,000 synthetic geotagged records clustered around
    8 major Indian metros, for hotspot-detection demos.

Regenerate synthetic data / retrain models at any time:
```
cd backend
venv/Scripts/python app/../data/scripts/generate_synthetic_datasets.py
venv/Scripts/python app/ml/train_models.py
```

## Architecture

- **Backend**: FastAPI + scikit-learn + pandas (Python 3.12)
- **Frontend**: React + Vite + Recharts

## Running locally

```
# Backend
cd backend
python -m venv venv
venv/Scripts/pip install -r requirements.txt
venv/Scripts/python data/scripts/generate_synthetic_datasets.py
venv/Scripts/python app/ml/train_models.py
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

## Tests

```
cd backend
venv/Scripts/python -m pytest tests/ -v
```
