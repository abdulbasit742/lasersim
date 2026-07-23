"""Adaptive decision improvement engine foundation for LaserSim autonomous AI."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class DecisionRecord:
    decision_id: str
    context: Dict[str, str]
    outcome: str
    score: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class AdaptiveDecisionImprovementEngine:
    """Stores decisions and improves future decision strategies."""

    def __init__(self):
        self.decisions: List[DecisionRecord] = []

    def record_decision(self, decision: DecisionRecord):
        self.decisions.append(decision)

    def improve_strategy(self, minimum_score: float = 0.0):
        return [
            decision
            for decision in self.decisions
            if decision.score >= minimum_score
        ]
