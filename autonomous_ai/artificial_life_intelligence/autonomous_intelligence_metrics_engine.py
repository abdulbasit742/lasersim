"""Autonomous intelligence metrics engine foundation."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class IntelligenceMetric:
    category: str
    score: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class AutonomousIntelligenceMetricsEngine:
    def __init__(self):
        self.metrics = []

    def add_metric(self, category: str, score: float):
        self.metrics.append(IntelligenceMetric(category, score))

    def average_score(self):
        if not self.metrics:
            return 0
        return sum(m.score for m in self.metrics) / len(self.metrics)
