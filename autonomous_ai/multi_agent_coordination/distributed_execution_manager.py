"""Distributed execution manager foundation for LaserSim.

Tracks autonomous execution requests across future agent clusters.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class ExecutionRequest:
    task_id: str
    assigned_agent: str
    status: str = "queued"


class DistributedExecutionManager:
    def __init__(self):
        self.requests: Dict[str, ExecutionRequest] = {}

    def register_execution(self, request: ExecutionRequest):
        self.requests[request.task_id] = request

    def update_status(self, task_id: str, status: str):
        if task_id in self.requests:
            self.requests[task_id].status = status
