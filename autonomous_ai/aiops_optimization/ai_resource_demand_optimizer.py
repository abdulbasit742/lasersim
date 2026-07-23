"""AI resource demand optimizer foundation for LaserSim AI."""

from dataclasses import dataclass


@dataclass
class ResourceDemand:
    resource: str
    expected_demand: float


class AIResourceDemandOptimizer:
    def __init__(self):
        self.demands = []

    def add_prediction(self, resource: str, expected_demand: float):
        demand = ResourceDemand(resource, expected_demand)
        self.demands.append(demand)
        return demand

    def optimize_resources(self):
        return sorted(self.demands, key=lambda item: item.expected_demand, reverse=True)
