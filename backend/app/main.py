from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import crime_analysis, datasets, forensics, nlp

app = FastAPI(
    title="India Crime Behaviour & Digital-Forensic Evidence Analysis Platform",
    description=(
        "AI-driven multilingual (English, Hindi, Bengali, Marathi, Tamil, Telugu) crime behaviour "
        "and digital-forensic evidence analysis API, built on real NCRB crime statistics and "
        "synthetic India-focused crime-report datasets."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(datasets.router)
app.include_router(nlp.router)
app.include_router(forensics.router)
app.include_router(crime_analysis.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
