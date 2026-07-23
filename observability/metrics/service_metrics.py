"""Service metrics foundation for LaserSim monitoring."""

class MetricsCollector:
    def __init__(self):
        self.metrics = {}

    def record(self, name, value):
        self.metrics[name] = value

    def snapshot(self):
        return dict(self.metrics)
