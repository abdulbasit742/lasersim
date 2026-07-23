"""Experiment result storage manager foundation."""

class ResultManager:
    def __init__(self):
        self.results = {}

    def save_result(self, experiment_id, result):
        self.results[experiment_id] = result

    def get_result(self, experiment_id):
        return self.results.get(experiment_id)
