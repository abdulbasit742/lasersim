"""Evolutionary pressure simulator foundation for LaserSim."""

from dataclasses import dataclass


@dataclass
class PressureEvent:
    environment: str
    pressure_level: float


class EvolutionaryPressureSimulator:
    def __init__(self):
        self.events = []

    def add_pressure_event(self, environment: str, pressure_level: float):
        self.events.append(
            PressureEvent(
                environment=environment,
                pressure_level=pressure_level,
            )
        )

    def get_pressure_events(self):
        return self.events
