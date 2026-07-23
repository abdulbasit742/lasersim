"""Autonomous Hyperparameter Optimization Engine
LaserSim self-tuning AI foundation.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class OptimizationTrial:
    parameters: Dict[str, float]
    score: float = 0.0


class AutonomousHyperparameterOptimizationEngine:
    def __init__(self):
        self.trials: List[OptimizationTrial] = []

    def add_trial(self, parameters: Dict[str, float], score: float):
        self.trials.append(OptimizationTrial(parameters, score))

    def best_trial(self):
        if not self.trials:
            return None
        return max(self.trials, key=lambda trial: trial.score)
