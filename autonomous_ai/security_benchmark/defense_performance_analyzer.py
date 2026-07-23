"""Defense performance analytics foundation."""


class DefensePerformanceAnalyzer:
    def __init__(self):
        self.metrics = []

    def record(self, defense_name, score):
        metric = {"defense": defense_name, "score": score}
        self.metrics.append(metric)
        return metric

    def best_strategy(self):
        if not self.metrics:
            return None
        return max(self.metrics, key=lambda item: item["score"])
