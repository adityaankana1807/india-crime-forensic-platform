"""
Criminal-behaviour analysis: builds per-suspect behavioural profiles from
linked incident sequences in the synthetic crime-report dataset (suspect_id /
mo_cluster / incident_index columns) — modus-operandi consistency, escalation
trend, and geographic spread. This is the platform's core "behaviour
analysis" module.
"""
import pandas as pd

from app.config import DATA_SYNTHETIC_DIR
from app.services import llm_service

REPORTS_PATH = DATA_SYNTHETIC_DIR / "crime_reports_multilingual.csv"
THREAT_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


def _load_linked() -> pd.DataFrame:
    df = pd.read_csv(REPORTS_PATH, keep_default_na=False, parse_dates=["date"])
    return df[df["suspect_id"] != ""].copy()


def list_profiles() -> list[dict]:
    df = _load_linked()
    profiles = []
    for suspect_id, group in df.groupby("suspect_id"):
        group = group.sort_values("date")
        severities = group["threat_level"].map(THREAT_ORDER).tolist()
        escalating = severities == sorted(severities) and severities[-1] > severities[0]
        dominant_crime_type = group["crime_type"].mode().iat[0]
        mo_consistency = round(float((group["crime_type"] == dominant_crime_type).mean()), 3)
        profiles.append({
            "suspect_id": suspect_id,
            "mo_cluster": group["mo_cluster"].iat[0],
            "language": group["language"].mode().iat[0],
            "incident_count": len(group),
            "dominant_crime_type": dominant_crime_type,
            "mo_consistency": mo_consistency,
            "first_incident_date": group["date"].min().date().isoformat(),
            "last_incident_date": group["date"].max().date().isoformat(),
            "locations_involved": sorted(group["location"].unique().tolist()),
            "escalating": bool(escalating),
            "current_threat_level": group.sort_values("date")["threat_level"].iat[-1],
        })
    profiles.sort(key=lambda p: (p["escalating"], p["incident_count"]), reverse=True)
    return profiles


def get_profile_detail(suspect_id: str) -> dict | None:
    df = _load_linked()
    group = df[df["suspect_id"] == suspect_id].sort_values("date")
    if group.empty:
        return None
    incidents = [
        {
            "date": row["date"].date().isoformat(),
            "crime_type": row["crime_type"],
            "threat_level": row["threat_level"],
            "location": row["location"],
            "text": row["text"],
        }
        for _, row in group.iterrows()
    ]
    profiles = {p["suspect_id"]: p for p in list_profiles()}
    profile = profiles.get(suspect_id, {})
    return {**profile, "incidents": incidents}


def generate_narrative(suspect_id: str) -> dict | None:
    detail = get_profile_detail(suspect_id)
    if detail is None:
        return None
    if not llm_service.is_available():
        return {"error": "LLM not configured (ANTHROPIC_API_KEY not set)"}
    incidents_for_llm = [
        {"date": i["date"], "crime_type": i["crime_type"], "threat_level": i["threat_level"], "location": i["location"]}
        for i in detail["incidents"]
    ]
    result = llm_service.generate_behavioral_narrative(suspect_id, incidents_for_llm)
    return result
