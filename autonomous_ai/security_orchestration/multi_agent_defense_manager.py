"""Multi-agent defense coordination foundation."""

class MultiAgentDefenseManager:
    def __init__(self):
        self.agents = {}

    def register_agent(self, name, agent):
        self.agents[name] = agent

    def dispatch(self, threat):
        return {
            "threat": threat,
            "agents_notified": list(self.agents.keys())
        }
