import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_list_datasets():
    r = client.get("/api/datasets")
    assert r.status_code == 200
    names = [d["name"] for d in r.json()]
    assert "crime_reports_multilingual.csv" in names
    assert "chicago_crime.csv" in names


def test_nlp_analyze_english():
    r = client.post("/api/nlp/analyze", json={"text": "Someone broke into the house near Andheri and stole a mobile phone and gold jewellery."})
    assert r.status_code == 200
    body = r.json()
    assert body["detected_language"] == "en"
    assert body["crime_type"] in {
        "theft", "burglary", "robbery", "dacoity", "murder", "kidnapping",
        "cybercrime", "cheating_fraud", "drug_trafficking", "crime_against_women",
        "extortion", "rioting",
    }
    assert body["threat_level"] in {"low", "medium", "high", "critical"}


def test_forensics_analyze():
    text = "Contact john.doe@example.com from IP 192.168.1.5, bring a gun on 2024-05-01."
    r = client.post("/api/forensics/analyze", json={"text": text})
    assert r.status_code == 200
    body = r.json()
    assert "john.doe@example.com" in body["entities"]["emails"]
    assert "192.168.1.5" in body["entities"]["ip_addresses"]
    assert "192.168.1.5" not in body["entities"]["phone_numbers"]
    assert "2024-05-01" not in body["entities"]["phone_numbers"]
    assert "gun" in body["risk_keywords"]
    assert body["risk_level"] in {"low", "medium", "high", "critical"}


def test_crime_hotspots():
    r = client.get("/api/crime-analysis/hotspots")
    assert r.status_code == 200
    body = r.json()
    assert body["cluster_count"] > 0


def test_crime_trends():
    r = client.get("/api/crime-analysis/trends")
    assert r.status_code == 200
    assert "by_crime_type" in r.json()


def test_sentiment_analyze():
    r = client.post("/api/sentiment/analyze", json={
        "text": "I think I'm being followed near Andheri, I'm really scared, please help me.",
        "use_llm": False,
    })
    assert r.status_code == 200
    body = r.json()
    assert body["baseline"]["tone"] in {"deceptive", "threatening", "neutral", "distressed"}
    assert body["llm"] is None


def test_behavior_profiles_list():
    r = client.get("/api/behavior/profiles")
    assert r.status_code == 200
    profiles = r.json()
    assert len(profiles) > 0
    assert "mo_consistency" in profiles[0]
    assert "escalating" in profiles[0]


def test_behavior_profile_detail():
    profiles = client.get("/api/behavior/profiles").json()
    suspect_id = profiles[0]["suspect_id"]
    r = client.get(f"/api/behavior/profiles/{suspect_id}")
    assert r.status_code == 200
    detail = r.json()
    assert detail["suspect_id"] == suspect_id
    assert len(detail["incidents"]) == detail["incident_count"]


def test_behavior_profile_not_found():
    r = client.get("/api/behavior/profiles/SUSP-9999")
    assert r.status_code == 404
