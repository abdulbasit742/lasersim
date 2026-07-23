"""LaserSim autonomous system health monitoring foundation."""

from datetime import datetime


class SystemHealthMonitor:
    def __init__(self):
        self.metrics = {}

    def record_metric(self, name, value):
        self.metrics[name] = {
            "value": value,
            "timestamp": datetime.utcnow().isoformat()
        }

    def health_snapshot(self):
        return self.metrics.copy()
