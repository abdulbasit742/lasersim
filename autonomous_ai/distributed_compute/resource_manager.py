"""Resource manager foundation for distributed LaserSim workloads."""

class ResourceManager:
    def __init__(self):
        self.resources = {}

    def register_resource(self, resource_id, resource_type, capacity):
        self.resources[resource_id] = {"type": resource_type, "capacity": capacity, "status": "available"}

    def get_available_resources(self):
        return {k: v for k, v in self.resources.items() if v["status"] == "available"}
