"""
AI Stability Forecasting System
Foundation layer for predicting future autonomous AI stability trends.
"""

from datetime import datetime


class AIStabilityForecastingSystem:
    def __init__(self):
        self.forecasts = []

    def create_forecast(self, system_id, stability_score, risk_level):
        record = {
            "system_id": system_id,
            "stability_score": stability_score,
            "risk_level": risk_level,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.forecasts.append(record)
        return record

    def latest_forecasts(self):
        return self.forecasts[-10:]
