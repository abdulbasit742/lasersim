"""AI motivation and priority scheduling foundation."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class MotivationTask:
    task_id: str
    importance: float
    urgency: float
    status: str = "pending"


class AIMotivationPriorityScheduler:
    def __init__(self):
        self.tasks: Dict[str, MotivationTask] = {}
        self.history: List[str] = []

    def add_task(self, task_id: str, importance: float, urgency: float):
        self.tasks[task_id] = MotivationTask(task_id, importance, urgency)

    def prioritize(self):
        return sorted(
            self.tasks.values(),
            key=lambda task: task.importance + task.urgency,
            reverse=True,
        )

    def record(self, event: str):
        self.history.append(event)
