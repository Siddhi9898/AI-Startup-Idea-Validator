"""
models.py
------------
Pydantic models for structured, validated agent outputs. Matches
the reference project's pattern (e.g. CompetitorResearch) - forcing
the LLM's output through a strict schema instead of trusting loose
JSON.parse() with no validation.
"""

from pydantic import BaseModel, Field
from typing import List


class Competitor(BaseModel):
    name: str
    strength: str = ""
    weakness: str = ""
    source_url: str = ""


class CompetitorResearch(BaseModel):
    direct_competitors: List[Competitor] = Field(default_factory=list)
    indirect_competitors: List[Competitor] = Field(default_factory=list)
    market_gap: str = ""
    competitive_intensity: str = "unknown"  # low / medium / high / unknown
