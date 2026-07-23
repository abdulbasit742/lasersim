"""Agent performance based scheduling foundation."""


class AgentPerformanceScheduler:
    def __init__(self):
        self.agents = {}

    def register_agent(self, agent_id, performance_score=0):
        self.agents[agent_id] = performance_score

    def select_best_agent(self):
        if not self.agents:
            return None
        return max(self.agents, key=self.agents.get)
