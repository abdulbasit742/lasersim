"""LaserSim model registry foundation.
Tracks model versions, metadata and deployment status.
"""

class ModelRegistry:
    def __init__(self):
        self.models = {}

    def register(self, name, version, metadata=None):
        self.models[f"{name}:{version}"] = {
            "metadata": metadata or {},
            "status": "registered"
        }
        return self.models[f"{name}:{version}"]

    def get(self, name, version):
        return self.models.get(f"{name}:{version}")
