"""Cognitive state monitoring foundation for autonomous AI."""

from dataclasses import dataclass
from typing import Dict


@dataclass
class CognitiveState:
    agent_id: str
    focus: float = 0.0
    confidence: float = 0.0
    stability: float = 0.0


class CognitiveStateMonitor:
    def __init__(self):
        self.states: Dict[str, CognitiveState] = {}

    def update_state(self, agent_id: str, focus: float, confidence: float, stability: float):
        self.states[agent_id] = CognitiveState(
            agent_id, focus, confidence, stability
        )

    def get_state(self, agent_id: str):
        return self.states.get(agent_id)
