"""Live beam experiment metrics layer."""

from dataclasses import dataclass


@dataclass
class BeamMetrics:
    power: float = 0.0
    stability: float = 0.0
    mode: str = "unknown"

    def as_dict(self):
        return {
            "power": self.power,
            "stability": self.stability,
            "mode": self.mode,
        }
