"""Recovery priority management foundation for LaserSim."""

class RecoveryPriorityManager:
    def __init__(self):
        self.priorities = []

    def add_priority(self, item):
        self.priorities.append(item)

    def rank(self):
        return self.priorities
