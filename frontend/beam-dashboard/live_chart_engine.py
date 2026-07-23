"""Live chart engine foundation for beam monitoring."""

class BeamMetricsChart:
    def __init__(self):
        self.history = []

    def add_metric(self, value):
        self.history.append(value)

    def latest(self):
        return self.history[-1] if self.history else None
