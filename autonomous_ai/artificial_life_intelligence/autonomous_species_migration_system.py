"""Autonomous species migration system foundation."""

from dataclasses import dataclass
from typing import List


@dataclass
class MigrationEvent:
    species_id: str
    source_environment: str
    target_environment: str


class AutonomousSpeciesMigrationSystem:
    def __init__(self):
        self.events: List[MigrationEvent] = []

    def migrate(self, event: MigrationEvent):
        self.events.append(event)

    def history(self):
        return self.events
