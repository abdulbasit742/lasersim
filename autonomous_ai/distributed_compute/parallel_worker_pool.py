"""Parallel worker pool foundation for simulation jobs."""

class WorkerPool:
    def __init__(self):
        self.workers = []

    def add_worker(self, worker):
        self.workers.append(worker)

    def available_workers(self):
        return [w for w in self.workers if getattr(w, "available", True)]
