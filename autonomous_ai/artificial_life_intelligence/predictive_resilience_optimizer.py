class PredictiveResilienceOptimizer:
    def __init__(self):
        self.predictions = []

    def record_prediction(self, system, risk_level, recommendation):
        event = {
            "system": system,
            "risk_level": risk_level,
            "recommendation": recommendation
        }
        self.predictions.append(event)
        return event

    def latest_prediction(self):
        return self.predictions[-1] if self.predictions else None
