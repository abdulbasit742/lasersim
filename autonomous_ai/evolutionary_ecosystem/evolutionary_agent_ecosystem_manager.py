class EvolutionaryAgentEcosystemManager:
    def __init__(self):
        self.populations = {}

    def register_population(self, name, agents):
        self.populations[name] = agents

    def evaluate_population(self, name):
        agents = self.populations.get(name, [])
        return {"population": name, "agents": len(agents)}
