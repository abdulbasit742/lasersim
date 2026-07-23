"""LaserSim AI anomaly detection foundation.

Detects abnormal beam/system behavior and provides hooks for
future ML-based fault classifiers.
"""

class AnomalyDetector:
    def __init__(self, threshold=0.1):
        self.threshold = threshold
        self.history = []

    def evaluate(self, expected, measured):
        error = abs(expected - measured)
        self.history.append(error)
        return {
            "error": error,
            "anomaly": error > self.threshold,
        }
