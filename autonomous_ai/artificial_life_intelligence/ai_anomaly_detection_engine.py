"""
AI Anomaly Detection Engine
Foundation layer for detecting unusual autonomous AI behavior.
"""

from datetime import datetime


class AIAnomalyDetectionEngine:
    def __init__(self):
        self.anomalies = []

    def record_anomaly(self, component, anomaly_type, severity):
        event = {
            "component": component,
            "anomaly_type": anomaly_type,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.anomalies.append(event)
        return event

    def get_recent_anomalies(self):
        return self.anomalies[-10:]
