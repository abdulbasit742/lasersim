"""Resilience scoring foundation for LaserSim recovery systems."""


class ResilienceScoringEngine:
    """Evaluates recovery readiness metrics."""

    def __init__(self):
        self.metrics = []

    def record_metric(self, name, value):
        self.metrics.append({"name": name, "value": value})

    def calculate_score(self):
        if not self.metrics:
            return 0
        return sum(item["value"] for item in self.metrics) / len(self.metrics)
