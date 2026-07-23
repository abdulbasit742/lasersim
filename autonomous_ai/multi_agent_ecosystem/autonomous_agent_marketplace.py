"""Autonomous agent marketplace foundation for LaserSim."""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class AgentCapability:
    agent_id: str
    capabilities: list[str] = field(default_factory=list)


class AutonomousAgentMarketplace:
    def __init__(self):
        self.agents: Dict[str, AgentCapability] = {}

    def register_agent(self, agent_id: str, capabilities: list[str]):
        self.agents[agent_id] = AgentCapability(agent_id, capabilities)

    def discover(self, capability: str):
        return [agent for agent in self.agents.values() if capability in agent.capabilities]
