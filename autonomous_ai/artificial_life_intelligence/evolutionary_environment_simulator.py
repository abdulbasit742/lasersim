"""Evolutionary environment simulator foundation.

Provides a base for testing adaptive AI populations.
"""

from dataclasses import dataclass


@dataclass
class EnvironmentState:
    name: str
    difficulty: int = 1


class EvolutionaryEnvironmentSimulator:
    def __init__(self):
        self.environments = []

    def create_environment(self, name: str, difficulty: int = 1):
        environment = EnvironmentState(name, difficulty)
        self.environments.append(environment)
        return environment

    def list_environments(self):
        return self.environments
