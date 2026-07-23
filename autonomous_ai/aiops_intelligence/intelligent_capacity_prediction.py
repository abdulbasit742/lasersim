"""Intelligent capacity prediction foundation for LaserSim."""

from datetime import datetime


class IntelligentCapacityPrediction:
    def __init__(self):
        self.capacity_predictions = []

    def predict_capacity(self, resource, expected_load):
        prediction = {
            "resource": resource,
            "expected_load": expected_load,
            "created_at": datetime.utcnow().isoformat(),
        }
        self.capacity_predictions.append(prediction)
        return prediction

    def history(self):
        return list(self.capacity_predictions)
