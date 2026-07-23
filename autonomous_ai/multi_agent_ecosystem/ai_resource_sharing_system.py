"""
AI Resource Sharing System
Foundation for autonomous agent resource exchange.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class ResourceAllocation:
    agent_id: str
    resource: str
    amount: float


class AIResourceSharingSystem:
    def __init__(self):
        self.allocations: Dict[str, ResourceAllocation] = {}

    def share_resource(self, agent_id: str, resource: str, amount: float):
        self.allocations[agent_id] = ResourceAllocation(
            agent_id=agent_id,
            resource=resource,
            amount=amount,
        )

    def get_allocation(self, agent_id: str):
        return self.allocations.get(agent_id)
