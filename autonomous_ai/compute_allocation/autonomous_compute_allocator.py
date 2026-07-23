"""Autonomous compute allocation foundation for LaserSim.

Provides a framework for tracking workloads and assigning compute resources.
"""

class AutonomousComputeAllocator:
    def __init__(self):
        self.resources = {}
        self.allocations = {}

    def register_resource(self, resource_id, capacity):
        self.resources[resource_id] = capacity

    def allocate(self, workload_id, resource_id):
        if resource_id in self.resources:
            self.allocations[workload_id] = resource_id
            return True
        return False

    def status(self):
        return {"resources": self.resources, "allocations": self.allocations}
