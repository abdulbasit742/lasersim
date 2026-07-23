"""
Agent Trust & Reputation Intelligence
Foundation module for autonomous multi-agent ecosystems.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class AgentReputation:
    agent_id: str
    trust_score: float = 1.0
    completed_tasks: int = 0


class AgentTrustReputationIntelligence:
    def __init__(self):
        self.agents: Dict[str, AgentReputation] = {}

    def register_agent(self, agent_id: str):
        self.agents[agent_id] = AgentReputation(agent_id=agent_id)

    def update_reputation(self, agent_id: str, success: bool):
        agent = self.agents[agent_id]
        agent.completed_tasks += 1
        if success:
            agent.trust_score = min(1.0, agent.trust_score + 0.05)
        else:
            agent.trust_score = max(0.0, agent.trust_score - 0.1)

    def get_trust_score(self, agent_id: str):
        return self.agents[agent_id].trust_score
