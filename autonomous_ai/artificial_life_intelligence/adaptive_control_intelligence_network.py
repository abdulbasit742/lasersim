"""Adaptive Control Intelligence Network foundation for LaserSim."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ControlSignal:
    source: str
    value: float


@dataclass
class AdaptiveControlIntelligenceNetwork:
    signals: List[ControlSignal] = field(default_factory=list)
    adjustments: List[Dict[str, float]] = field(default_factory=list)

    def register_signal(self, source: str, value: float) -> None:
        self.signals.append(ControlSignal(source, value))

    def record_adjustment(self, parameter: str, score: float) -> None:
        self.adjustments.append({"parameter": parameter, "score": score})

    def latest_state(self) -> Dict[str, int]:
        return {
            "signals": len(self.signals),
            "adjustments": len(self.adjustments),
        }
