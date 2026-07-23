"""Experiment database schema foundation for LaserSim."""

EXPERIMENT_FIELDS = [
    "experiment_id",
    "user_id",
    "created_at",
    "beam_parameters",
    "model_version",
    "results",
]

class ExperimentRecord:
    def __init__(self, experiment_id, user_id, results=None):
        self.experiment_id = experiment_id
        self.user_id = user_id
        self.results = results or {}
