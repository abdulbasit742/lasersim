"""Autonomous experiment task scheduling foundation for LaserSim."""

class TaskScheduler:
    def __init__(self):
        self.queue = []

    def add_task(self, task):
        self.queue.append(task)
        return task

    def next_task(self):
        if self.queue:
            return self.queue.pop(0)
        return None
