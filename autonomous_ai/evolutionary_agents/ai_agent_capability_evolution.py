"""AI agent capability evolution foundation for LaserSim."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class AgentCapabilityEvolution:
    capabilities: Dict[str, List[str]] = field(default_factory=dict)

    def register_capability(self, agent_id: str, capability: str) -> None:
        self.capabilities.setdefault(agent_id, []).append(capability)

    def evolve_capability(self, agent_id: str, improvement: str) -> None:
        self.capabilities.setdefault(agent_id, []).append(improvement)

    def get_capabilities(self, agent_id: str) -> List[str]:
        return self.capabilities.get(agent_id, [])
