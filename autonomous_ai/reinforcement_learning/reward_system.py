"""Reward calculation foundation for autonomous beam optimization."""

class BeamOptimizationReward:
    def calculate(self, metrics):
        stability = metrics.get("stability", 0)
        accuracy = metrics.get("accuracy", 0)
        return stability + accuracy
