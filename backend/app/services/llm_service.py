"""
Wraps the Anthropic Claude API for the platform's LLM-driven analysis:
LLM-based structured entity extraction, sentiment/intent reasoning, and
qualitative behavioural-profile narrative generation. Requires
ANTHROPIC_API_KEY to be set (see backend/.env.example); every function
degrades to a clear "unavailable" result rather than raising if the key is
missing or the API call fails, so the rest of the platform keeps working
without it.
"""
import json
import os

from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-4-5"
_client = None


def _get_client():
    global _client
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    if _client is None:
        import anthropic
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def is_available() -> bool:
    return _get_client() is not None


def _call_json(prompt: str, max_tokens: int = 1024) -> dict | None:
    client = _get_client()
    if client is None:
        return None
    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.content[0].text.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}


def extract_entities_llm(text: str) -> dict | None:
    prompt = f"""You are assisting a digital-forensics analyst. Extract structured information from the evidence text below, which may be in English, Hindi, Bengali, Marathi, Tamil, or Telugu.

Return ONLY a JSON object with these keys:
- "persons": list of person names mentioned
- "locations": list of place names mentioned
- "organizations": list of organizations mentioned (if any)
- "weapons_or_items": list of weapons or notable items mentioned
- "dates_or_times": list of dates/times mentioned
- "offence_indicators": list of short phrases indicating what offence(s) may be involved
- "summary_english": one-sentence English summary of the text, regardless of its original language

Evidence text:
\"\"\"{text}\"\"\"

Return only the JSON object, no other text."""
    return _call_json(prompt, max_tokens=800)


def analyze_sentiment_llm(text: str) -> dict | None:
    prompt = f"""You are assisting a digital-forensics analyst with sentiment/intent analysis of evidence text (chat logs, messages, reports), which may be in English, Hindi, Bengali, Marathi, Tamil, or Telugu.

Classify the emotional tone of the text below into exactly one of: "deceptive", "threatening", "neutral", "distressed".

Return ONLY a JSON object with keys:
- "tone": one of the four labels above
- "intensity": integer 1-5 (5 = most intense)
- "rationale": one-sentence explanation in English of why you chose this label

Text:
\"\"\"{text}\"\"\"

Return only the JSON object, no other text."""
    return _call_json(prompt, max_tokens=400)


def generate_behavioral_narrative(suspect_id: str, incidents: list[dict]) -> dict | None:
    incidents_json = json.dumps(incidents, ensure_ascii=False, indent=2)
    prompt = f"""You are assisting a crime analyst in writing a qualitative behavioural-pattern summary for an internal case review. Below is a structured incident history for suspect {suspect_id}, drawn from police report records.

Incident history (chronological):
{incidents_json}

Write a behavioural analysis covering: (1) modus operandi consistency, (2) any escalation or de-escalation trend in severity over time, (3) geographic pattern, (4) an overall risk-trajectory assessment. Keep it factual and grounded only in the data given — do not invent facts not present in the incident history.

Return ONLY a JSON object with keys:
- "modus_operandi_summary": string
- "escalation_assessment": string
- "geographic_pattern": string
- "risk_trajectory": one of "declining", "stable", "escalating"
- "narrative": a 3-5 sentence overall summary in English

Return only the JSON object, no other text."""
    return _call_json(prompt, max_tokens=900)
