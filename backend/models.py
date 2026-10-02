"""
models.py
=========
Pydantic models define the "shape" of data going in and out of the API.
Request models are unchanged. Response models now reflect the structured
recommendation layout produced by renderer.py.
"""

from pydantic import BaseModel
from typing import Optional


class MatchRequest(BaseModel):
    """What the frontend sends when the user submits the structured form."""
    plant: str
    problem: str
    affected_part: Optional[str] = None
    environment: Optional[str] = None
    season: Optional[str] = None
    growing_condition: Optional[str] = None
    language: Optional[str] = "en"


class FreeTextRequest(BaseModel):
    """What the frontend sends when the user types/speaks a free-text description."""
    text: str
    language: Optional[str] = "en"


class FeedbackRequest(BaseModel):
    """Simple usefulness feedback (Section 24 Screen 7)."""
    case_id: str
    was_useful: bool
    comment: Optional[str] = None


# --- Response models (documentation / OpenAPI only; not strictly enforced) ---

class IKSPrinciple(BaseModel):
    statement: str
    source_type: str
    source_note: str


class IKSPractice(BaseModel):
    name: str
    description: str
    source_type: str
    primary_citation: str
    secondary_citation: Optional[str] = None
    modern_evidence: Optional[str] = None
    evidence_level: Optional[str] = None


class IKSSeasonal(BaseModel):
    name: str
    description: str
    source_type: str
    source_citation: str
    verification_status: str


class IKSBlock(BaseModel):
    principle: Optional[IKSPrinciple] = None
    specific_practice: Optional[IKSPractice] = None
    seasonal_principle: Optional[IKSSeasonal] = None
    relevance_to_this_case: Optional[str] = None
    verification_status: Optional[str] = None


class SustainableOption(BaseModel):
    action: str
    cost: str
    availability: str


class RecommendationResponse(BaseModel):
    matched: bool
    confidence: str
    problem_summary: str
    priority_actions: list[str]
    sustainable_options: list[SustainableOption]
    iks: IKSBlock
    connection: str
    monitor: str
    seek_expert_if: list[str]
    why: str
    sources: list[str]
    symptoms: list[str]
    sources_verification_status: str