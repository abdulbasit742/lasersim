"""Civilization security and protection layer foundation."""

from dataclasses import dataclass
from typing import List


@dataclass
class SecurityEvent:
    civilization: str
    event_type: str
    severity: str = "low"


class CivilizationSecurityProtectionLayer:
    def __init__(self):
        self.events: List[SecurityEvent] = []

    def register_event(self, civilization: str, event_type: str, severity: str = "low"):
        event = SecurityEvent(civilization, event_type, severity)
        self.events.append(event)
        return event

    def get_events(self):
        return [event.__dict__ for event in self.events]
