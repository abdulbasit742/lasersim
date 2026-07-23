"""Background AI worker management foundation."""

class WorkerManager:
    def __init__(self):
        self.workers = {}

    def register_worker(self, name, worker):
        self.workers[name] = worker

    def get_worker(self, name):
        return self.workers.get(name)
