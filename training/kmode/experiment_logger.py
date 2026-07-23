from datetime import datetime


class ExperimentLogger:
    def __init__(self):
        self.start_time = datetime.now()
        self.metrics = {}

    def log(self, name, value):
        self.metrics[name] = value

    def summary(self):
        return {
            'started': self.start_time.isoformat(),
            'metrics': self.metrics,
        }
