"""Autonomous decision intelligence engine foundation."""

from dataclasses import dataclass
from typing import List


@dataclass
class DecisionRecord:
    situation: str
    decision: str
    confidence: float


class AutonomousDecisionIntelligenceEngine:
    def __init__(self):
        self.decisions: List[DecisionRecord] = []

    def evaluate(self, situation: str, decision: str, confidence: float):
        record = DecisionRecord(situation, decision, confidence)
        self.decisions.append(record)
        return record

    def highest_confidence_decision(self):
        if not self.decisions:
            return None
        return max(self.decisions, key=lambda item: item.confidence)
