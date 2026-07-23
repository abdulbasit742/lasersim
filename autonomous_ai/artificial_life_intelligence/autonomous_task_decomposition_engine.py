"""Autonomous task decomposition foundation for LaserSim AI systems."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class TaskPlan:
    goal: str
    subtasks: List[str] = field(default_factory=list)


class AutonomousTaskDecompositionEngine:
    def __init__(self):
        self.plans = []

    def create_plan(self, goal: str, subtasks: List[str]):
        plan = TaskPlan(goal=goal, subtasks=subtasks)
        self.plans.append(plan)
        return plan
