"""AI Healing Strategy Generator foundation for LaserSim."""

class AIHealingStrategyGenerator:
    def __init__(self):
        self.strategies = []

    def add_strategy(self, name, effectiveness):
        self.strategies.append({
            "name": name,
            "effectiveness": effectiveness,
        })

    def best_strategy(self):
        if not self.strategies:
            return None
        return max(self.strategies, key=lambda item: item["effectiveness"])
