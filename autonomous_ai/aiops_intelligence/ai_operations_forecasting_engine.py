"""AI Operations Forecasting Engine foundation for LaserSim."""

from datetime import datetime


class AIOperationsForecastingEngine:
    def __init__(self):
        self.forecasts = []

    def create_forecast(self, metric, prediction, confidence=0.0):
        record = {
            "metric": metric,
            "prediction": prediction,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.forecasts.append(record)
        return record

    def get_forecasts(self):
        return list(self.forecasts)
