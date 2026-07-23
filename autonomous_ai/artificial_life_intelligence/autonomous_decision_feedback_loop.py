"""Autonomous decision feedback loop foundation.

Provides a lightweight framework for recording decision outcomes
and improving future autonomous decisions.
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DecisionFeedback:
    decision_id: str
    score: float
    feedback: str


class AutonomousDecisionFeedbackLoop:
    def __init__(self) -> None:
        self.feedback_history: List[DecisionFeedback] = []

    def record_feedback(self, decision_id: str, score: float, feedback: str) -> None:
        self.feedback_history.append(
            DecisionFeedback(decision_id, score, feedback)
        )

    def best_decision(self) -> Dict[str, object]:
        if not self.feedback_history:
            return {}
        best = max(self.feedback_history, key=lambda item: item.score)
        return {
            "decision_id": best.decision_id,
            "score": best.score,
            "feedback": best.feedback,
        }
