"""
AI Governance Feedback Accelerator
Foundation layer for governance feedback improvement cycles.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class GovernanceFeedback:
    policy_id: str
    reward: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class AIGovernanceFeedbackAccelerator:
    def __init__(self):
        self.feedback_history: List[GovernanceFeedback] = []

    def add_feedback(self, policy_id: str, reward: float):
        self.feedback_history.append(GovernanceFeedback(policy_id, reward))

    def highest_reward(self):
        if not self.feedback_history:
            return None
        return max(self.feedback_history, key=lambda item: item.reward)
