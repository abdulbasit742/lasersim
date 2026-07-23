"""Self-improving strategy optimization foundation for LaserSim."""

from typing import Dict


class SelfImprovingStrategyOptimizer:
    def __init__(self):
        self.strategies: Dict[str, Dict] = {}

    def register_strategy(self, strategy_id: str, score: float = 0.0):
        self.strategies[strategy_id] = {"score": score, "iterations": 0}
        return self.strategies[strategy_id]

    def improve_strategy(self, strategy_id: str, improvement: float):
        if strategy_id in self.strategies:
            self.strategies[strategy_id]["score"] += improvement
            self.strategies[strategy_id]["iterations"] += 1
        return self.strategies.get(strategy_id)
