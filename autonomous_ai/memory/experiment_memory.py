"""Experiment memory foundation for LaserSim autonomous agents."""

class ExperimentMemory:
    def __init__(self):
        self.records = []

    def store(self, experiment):
        self.records.append(experiment)

    def retrieve_recent(self, limit=10):
        return self.records[-limit:]
