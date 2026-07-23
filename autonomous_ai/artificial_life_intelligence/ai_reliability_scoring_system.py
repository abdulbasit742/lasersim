"""AI Reliability Scoring System foundation for LaserSim."""

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class ReliabilityScore:
    component: str
    score: float
    created_at: str


class AIReliabilityScoringSystem:
    def __init__(self):
        self.scores: List[ReliabilityScore] = []

    def record_score(self, component: str, score: float):
        self.scores.append(
            ReliabilityScore(component, score, datetime.utcnow().isoformat())
        )

    def get_latest_scores(self):
        return self.scores[-10:]
