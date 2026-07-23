"""Civilization resilience optimizer foundation.

Tracks resilience improvement strategies for AI civilizations.
"""

from dataclasses import dataclass, field


@dataclass
class ResilienceRecord:
    civilization_id: str
    strategy: str
    score: float


class CivilizationResilienceOptimizer:
    def __init__(self):
        self.records: list[ResilienceRecord] = []

    def evaluate_strategy(self, civilization_id: str, strategy: str, score: float):
        record = ResilienceRecord(civilization_id, strategy, score)
        self.records.append(record)
        return record

    def best_strategy(self, civilization_id: str):
        matches = [r for r in self.records if r.civilization_id == civilization_id]
        if not matches:
            return None
        return max(matches, key=lambda item: item.score)
