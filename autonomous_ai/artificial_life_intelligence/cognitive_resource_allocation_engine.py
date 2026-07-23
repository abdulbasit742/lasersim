"""Cognitive resource allocation engine foundation."""

from datetime import datetime


class CognitiveResourceAllocationEngine:
    def __init__(self):
        self.resources = {}
        self.allocations = []

    def register_resource(self, name, capacity):
        self.resources[name] = {"capacity": capacity, "available": capacity}

    def allocate(self, resource, task, amount):
        entry = {
            "resource": resource,
            "task": task,
            "amount": amount,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.allocations.append(entry)
        return entry

    def get_status(self):
        return {
            "resources": self.resources,
            "allocations": self.allocations,
        }
