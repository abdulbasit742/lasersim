"""Experiment planning agent foundation for LaserSim autonomous AI."""

class ExperimentPlannerAgent:
    def __init__(self):
        self.goals = []

    def create_plan(self, objective):
        return {
            "objective": objective,
            "steps": [],
            "status": "planned"
        }
