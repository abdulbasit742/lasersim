"""Collective intelligence foundation for cooperating AI agents."""


class CollectiveIntelligenceEngine:
    def __init__(self):
        self.agent_contributions = []

    def register_contribution(self, agent_id, contribution):
        self.agent_contributions.append({
            "agent_id": agent_id,
            "contribution": contribution
        })

    def get_collective_state(self):
        return self.agent_contributions
