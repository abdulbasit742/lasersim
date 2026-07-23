"""AI cognitive performance analytics dashboard foundation."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CognitiveMetric:
    metric_name: str
    value: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class AICognitivePerformanceAnalyticsDashboard:
    def __init__(self):
        self.metrics = []

    def record_metric(self, metric_name: str, value: float):
        self.metrics.append(CognitiveMetric(metric_name, value))

    def latest_metrics(self):
        return self.metrics[-10:]
