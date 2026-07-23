"""Recovery Strategy Evolution Network foundation.

Tracks recovery strategies and evolution cycles for adaptive AI reliability.
"""


class RecoveryStrategyEvolutionNetwork:
    def __init__(self):
        self.strategies = []

    def register_strategy(self, strategy, score=0.0):
        record = {"strategy": strategy, "score": score}
        self.strategies.append(record)
        return record

    def best_strategy(self):
        if not self.strategies:
            return None
        return max(self.strategies, key=lambda item: item["score"])
