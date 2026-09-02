from typing import Optional

from pydantic import BaseModel, Field


class NlpAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    translate_to: Optional[str] = Field(default=None, description="Target language code, e.g. 'en'")


class NlpAnalyzeResponse(BaseModel):
    text: str
    detected_language: str
    detected_language_name: str
    language_confidence: float
    translated_text: Optional[str] = None
    crime_type: str
    threat_level: str
    threat_level_confidence: float
    keyword_flags: list[str]
    transformer_crime_type: Optional[str] = None
    transformer_confidence: Optional[float] = None


class ForensicAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=20000)
    source: Optional[str] = "unspecified"
    use_llm: bool = False


class ForensicEntities(BaseModel):
    emails: list[str]
    ip_addresses: list[str]
    phone_numbers: list[str]
    urls: list[str]
    dates: list[str]


class ForensicAnalyzeResponse(BaseModel):
    sha256: str
    detected_language: str
    entities: ForensicEntities
    risk_keywords: list[str]
    risk_score: int
    risk_level: str
    llm_extraction: Optional[dict] = None


class SentimentAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    use_llm: bool = True


class BehavioralNarrativeRequest(BaseModel):
    suspect_id: str


class DatasetInfo(BaseModel):
    name: str
    category: str
    rows: int
    columns: list[str]
    size_bytes: int


class DatasetStats(BaseModel):
    name: str
    rows: int
    columns: list[str]
    null_counts: dict[str, int]
    preview: list[dict]
