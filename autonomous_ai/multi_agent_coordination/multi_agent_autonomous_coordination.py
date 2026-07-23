"""
Multi Agent Autonomous Coordination foundation.
Provides a lightweight coordination registry for future agent collaboration.
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class AgentTask:
    agent_id: str
    objective: str
    status: str = "pending"


class MultiAgentCoordinator:
    def __init__(self):
        self.agents: Dict[str, Dict] = {}
        self.tasks: List[AgentTask] = []

    def register_agent(self, agent_id: str, capability: str):
        self.agents[agent_id] = {"capability": capability, "active": True}

    def assign_task(self, agent_id: str, objective: str):
        task = AgentTask(agent_id=agent_id, objective=objective)
        self.tasks.append(task)
        return task

    def get_active_agents(self):
        return [agent for agent in self.agents if self.agents[agent]["active"]]
