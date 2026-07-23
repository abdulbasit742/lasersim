"""Adaptive control learning accelerator foundation.

Tracks control learning cycles and improvement measurements.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class LearningCycle:
    cycle_name: str
    improvement_score: float


class AdaptiveControlLearningAccelerator:
    def __init__(self) -> None:
        self.cycles: List[LearningCycle] = []

    def add_cycle(self, cycle_name: str, improvement_score: float) -> None:
        self.cycles.append(LearningCycle(cycle_name, improvement_score))

    def best_cycle(self):
        if not self.cycles:
            return None
        return max(self.cycles, key=lambda cycle: cycle.improvement_score)
