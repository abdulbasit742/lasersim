"""Autonomous agent hierarchy foundation.

Provides role and priority management for AI agents.
"""

class AutonomousAgentHierarchySystem:
    def __init__(self):
        self.agents = {}

    def register_agent(self, agent_id: str, role: str, priority: int = 0):
        self.agents[agent_id] = {
            "role": role,
            "priority": priority,
        }

    def get_agent(self, agent_id: str):
        return self.agents.get(agent_id)
