"""LaserSim Prometheus metrics exporter foundation."""

from time import time


class PrometheusExporter:
    def __init__(self):
        self.metrics = {}

    def update_metric(self, name, value):
        self.metrics[name] = {
            "value": value,
            "timestamp": time(),
        }

    def export(self):
        return self.metrics
