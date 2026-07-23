"""AI agent selection system foundation for workload matching."""

class AIAgentSelectionSystem:
    def __init__(self):
        self.agents = []

    def register_agent(self, agent):
        self.agents.append(agent)
        return agent

    def available_agents(self):
        return list(self.agents)
