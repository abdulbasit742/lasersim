"""Security regression tracking foundation."""


class SecurityRegressionTracker:
    def __init__(self):
        self.baselines = {}
        self.results = []

    def set_baseline(self, name, score):
        self.baselines[name] = score

    def record_result(self, name, score):
        baseline = self.baselines.get(name)
        self.results.append({
            "test": name,
            "score": score,
            "baseline": baseline,
            "regression": baseline is not None and score < baseline,
        })
        return self.results[-1]
