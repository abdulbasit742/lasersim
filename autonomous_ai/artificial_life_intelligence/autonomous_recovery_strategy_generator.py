"""Autonomous recovery strategy generator foundation."""

from dataclasses import dataclass
from typing import List


@dataclass
class RecoveryStrategy:
    name: str
    success_rate: float


class AutonomousRecoveryStrategyGenerator:
    def __init__(self):
        self.strategies: List[RecoveryStrategy] = []

    def register_strategy(self, name: str, success_rate: float):
        self.strategies.append(RecoveryStrategy(name, success_rate))

    def best_strategy(self):
        if not self.strategies:
            return None
        return max(self.strategies, key=lambda item: item.success_rate)
