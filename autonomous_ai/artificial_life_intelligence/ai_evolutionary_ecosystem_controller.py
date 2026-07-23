"""AI Evolutionary Ecosystem Controller foundation."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class EcosystemState:
    populations: Dict[str, int] = field(default_factory=dict)
    stability_score: float = 0.0


class AIEvolutionaryEcosystemController:
    def __init__(self):
        self.states: List[EcosystemState] = []

    def record_state(self, state: EcosystemState):
        self.states.append(state)

    def latest_state(self):
        return self.states[-1] if self.states else None
