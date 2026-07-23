"""Evolutionary strategy optimizer foundation for autonomous agents."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class StrategyVariant:
    name: str
    score: float = 0.0


@dataclass
class EvolutionaryStrategyOptimizer:
    strategies: List[StrategyVariant] = field(default_factory=list)

    def add_strategy(self, name: str, score: float = 0.0) -> StrategyVariant:
        strategy = StrategyVariant(name, score)
        self.strategies.append(strategy)
        return strategy

    def best_strategy(self) -> StrategyVariant | None:
        if not self.strategies:
            return None
        return max(self.strategies, key=lambda item: item.score)
