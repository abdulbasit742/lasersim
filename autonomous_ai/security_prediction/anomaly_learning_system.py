"""Learning layer for security anomaly pattern detection."""


class AnomalyLearningSystem:
    def __init__(self):
        self.patterns = []

    def learn_pattern(self, data):
        self.patterns.append(data)

    def detect(self, observation):
        return {
            "observation": observation,
            "known_patterns": len(self.patterns),
            "anomaly": False,
        }
