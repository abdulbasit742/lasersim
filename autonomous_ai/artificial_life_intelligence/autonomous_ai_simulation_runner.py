"""Autonomous AI Simulation Runner
Post-200 execution layer for LaserSim.
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SimulationRun:
    name: str
    status: str = "created"
    metrics: Dict[str, float] = field(default_factory=dict)


class AutonomousAISimulationRunner:
    def __init__(self):
        self.runs: Dict[str, SimulationRun] = {}

    def create_run(self, name: str):
        self.runs[name] = SimulationRun(name=name)

    def execute_run(self, name: str):
        if name in self.runs:
            self.runs[name].status = "running"

    def record_metrics(self, name: str, metrics: Dict[str, float]):
        if name in self.runs:
            self.runs[name].metrics.update(metrics)

    def get_status(self):
        return {name: run.status for name, run in self.runs.items()}
