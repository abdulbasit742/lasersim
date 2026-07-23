"""Reliability intelligence fusion network foundation."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ReliabilitySignal:
    source: str
    score: float
    metadata: Dict[str, str] = field(default_factory=dict)


class ReliabilityIntelligenceFusionNetwork:
    def __init__(self):
        self.signals: List[ReliabilitySignal] = []

    def add_signal(self, source: str, score: float, metadata=None):
        self.signals.append(
            ReliabilitySignal(source, score, metadata or {})
        )

    def fused_reliability_score(self):
        if not self.signals:
            return 0.0
        return sum(signal.score for signal in self.signals) / len(self.signals)
