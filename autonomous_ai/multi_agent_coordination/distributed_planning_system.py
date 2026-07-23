"""
Distributed Planning System foundation.
Coordinates planning requests across autonomous components.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class PlanningRequest:
    source: str
    goal: str
    priority: int = 1


class DistributedPlanner:
    def __init__(self):
        self.requests: List[PlanningRequest] = []

    def add_request(self, source: str, goal: str, priority: int = 1):
        request = PlanningRequest(source, goal, priority)
        self.requests.append(request)
        return request

    def get_prioritized_requests(self):
        return sorted(self.requests, key=lambda item: item.priority, reverse=True)
