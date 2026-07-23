"""AI Governance Self Learning Optimizer foundation for LaserSim."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class GovernanceLearningRecord:
    policy: str
    reward: float


@dataclass
class AIGovernanceSelfLearningOptimizer:
    records: List[GovernanceLearningRecord] = field(default_factory=list)

    def add_learning_record(self, policy: str, reward: float) -> None:
        self.records.append(GovernanceLearningRecord(policy, reward))

    def best_policy(self) -> Dict[str, float]:
        if not self.records:
            return {}
        best = max(self.records, key=lambda item: item.reward)
        return {"policy": best.policy, "reward": best.reward}
