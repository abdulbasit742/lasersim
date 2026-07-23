"""AI-driven infrastructure decision foundation for LaserSim."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class InfrastructureDecision:
    signal: str
    decision: str
    created_at: str


class AIDrivenInfrastructureDecisionEngine:
    def __init__(self):
        self.decisions = []

    def evaluate(self, signal: str, decision: str):
        item = InfrastructureDecision(
            signal=signal,
            decision=decision,
            created_at=datetime.utcnow().isoformat(),
        )
        self.decisions.append(item)
        return item

    def get_decisions(self):
        return self.decisions
