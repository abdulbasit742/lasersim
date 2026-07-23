"""Autonomous Governance Learning Engine

Foundation module for learning from governance decisions.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class GovernanceLearningRecord:
    policy_id: str
    reward: float


class AutonomousGovernanceLearningEngine:
    def __init__(self):
        self.history: List[GovernanceLearningRecord] = []

    def learn(self, policy_id: str, reward: float):
        self.history.append(GovernanceLearningRecord(policy_id, reward))

    def best_policy(self):
        if not self.history:
            return None
        return max(self.history, key=lambda item: item.reward)
