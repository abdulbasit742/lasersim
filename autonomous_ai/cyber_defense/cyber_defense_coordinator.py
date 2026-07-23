"""Cyber defense coordination foundation for LaserSim."""

from dataclasses import dataclass


@dataclass
class DefenseEvent:
    source: str
    severity: str
    description: str


class CyberDefenseCoordinator:
    """Coordinates safe defensive responses to security events."""

    def __init__(self):
        self.events = []

    def register_event(self, event: DefenseEvent):
        self.events.append(event)
        return event

    def evaluate(self, event: DefenseEvent):
        if event.severity.lower() in {"high", "critical"}:
            return "requires_response"
        return "monitor"
