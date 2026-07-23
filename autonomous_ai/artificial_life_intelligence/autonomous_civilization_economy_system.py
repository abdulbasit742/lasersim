"""Autonomous AI civilization economy system foundation.

Tracks resource exchanges and economic events between AI entities.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class EconomyEvent:
    source: str
    target: str
    resource: str
    amount: float


@dataclass
class AutonomousCivilizationEconomy:
    events: List[EconomyEvent] = field(default_factory=list)

    def record_exchange(self, event: EconomyEvent) -> None:
        self.events.append(event)
