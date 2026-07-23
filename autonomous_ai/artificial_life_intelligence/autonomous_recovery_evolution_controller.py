"""Autonomous recovery evolution controller foundation."""

from dataclasses import dataclass
from typing import List


@dataclass
class RecoveryEvolution:
    strategy: str
    improvement: float


class AutonomousRecoveryEvolutionController:
    def __init__(self):
        self.evolutions: List[RecoveryEvolution] = []

    def record_evolution(self, strategy: str, improvement: float):
        self.evolutions.append(RecoveryEvolution(strategy, improvement))

    def best_strategy(self):
        if not self.evolutions:
            return None
        return max(self.evolutions, key=lambda item: item.improvement)
