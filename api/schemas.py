"""Request/response schema definitions for beam API."""

from dataclasses import dataclass
from typing import List

@dataclass
class BeamPredictionRequest:
    features: List[float]

@dataclass
class BeamPredictionResponse:
    mode: str
    confidence: float
