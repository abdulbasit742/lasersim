class CollectiveAgentEvolutionIntelligence:
    def __init__(self):
        self.evolution_events = []

    def record_evolution(self, agent_group, improvement):
        self.evolution_events.append({
            "agent_group": agent_group,
            "improvement": improvement
        })

    def history(self):
        return self.evolution_events
