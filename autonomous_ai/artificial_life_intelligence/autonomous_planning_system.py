"""Autonomous planning system foundation."""

from dataclasses import dataclass
from typing import List


@dataclass
class Plan:
    objective: str
    steps: List[str]


class AutonomousPlanningSystem:
    def __init__(self):
        self.plans: List[Plan] = []

    def create_plan(self, objective: str, steps: List[str]):
        plan = Plan(objective, steps)
        self.plans.append(plan)
        return plan

    def get_plans(self):
        return self.plans
