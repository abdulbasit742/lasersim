"""Coordinator for multiple autonomous LaserSim agents."""

class AgentCoordinator:
    def __init__(self):
        self.agents = []

    def register(self, agent):
        self.agents.append(agent)

    def coordinate(self, task):
        return {
            "task": task,
            "agents": len(self.agents),
            "status": "coordinated"
        }
