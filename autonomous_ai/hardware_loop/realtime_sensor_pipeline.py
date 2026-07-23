"""Real-time sensor data pipeline foundation for LaserSim hardware loop."""

from datetime import datetime


class SensorPipeline:
    def __init__(self):
        self.samples = []

    def ingest(self, sensor_data):
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "data": sensor_data,
        }
        self.samples.append(record)
        return record

    def latest(self):
        return self.samples[-1] if self.samples else None
