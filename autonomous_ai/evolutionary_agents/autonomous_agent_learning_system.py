"""Autonomous agent learning system foundation for LaserSim."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class AutonomousAgentLearningSystem:
    experiences: Dict[str, List[str]] = field(default_factory=dict)

    def record_experience(self, agent_id: str, experience: str) -> None:
        self.experiences.setdefault(agent_id, []).append(experience)

    def learn_from_experience(self, agent_id: str) -> List[str]:
        return self.experiences.get(agent_id, [])
