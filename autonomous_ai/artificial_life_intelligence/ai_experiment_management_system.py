"""AI Experiment Management System
LaserSim continuous improvement foundation.
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Experiment:
    name: str
    status: str = "created"
    metrics: Dict[str, float] = field(default_factory=dict)


class AIExperimentManagementSystem:
    def __init__(self):
        self.experiments: List[Experiment] = []

    def create_experiment(self, name: str):
        experiment = Experiment(name=name)
        self.experiments.append(experiment)
        return experiment

    def update_metrics(self, name: str, metrics: Dict[str, float]):
        for experiment in self.experiments:
            if experiment.name == name:
                experiment.metrics.update(metrics)

    def summary(self):
        return [experiment.__dict__ for experiment in self.experiments]
