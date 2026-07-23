"""Artificial life learning loop foundation for LaserSim."""

from datetime import datetime


class ArtificialLifeLearningLoop:
    def __init__(self):
        self.learning_cycles = []

    def record_cycle(self, population, environment, outcome):
        cycle = {
            "population": population,
            "environment": environment,
            "outcome": outcome,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.learning_cycles.append(cycle)
        return cycle

    def get_cycles(self):
        return list(self.learning_cycles)
