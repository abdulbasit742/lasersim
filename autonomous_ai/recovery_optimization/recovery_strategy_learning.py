"""Recovery strategy learning foundation for LaserSim."""


class RecoveryStrategyLearning:
    def __init__(self):
        self.history = []

    def record_result(self, strategy, result):
        self.history.append({"strategy": strategy, "result": result})

    def recommend(self):
        return self.history[-1] if self.history else None
