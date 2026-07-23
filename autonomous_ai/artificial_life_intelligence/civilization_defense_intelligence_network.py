"""Civilization Defense Intelligence Network foundation."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class DefenseEvent:
    civilization_id: str
    event_type: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class CivilizationDefenseIntelligenceNetwork:
    def __init__(self):
        self.events: List[DefenseEvent] = []

    def register_event(self, civilization_id: str, event_type: str) -> DefenseEvent:
        event = DefenseEvent(civilization_id, event_type)
        self.events.append(event)
        return event

    def history(self) -> List[DefenseEvent]:
        return self.events
