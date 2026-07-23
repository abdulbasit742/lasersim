"""Distributed cluster management foundation for LaserSim."""

class ClusterManager:
    def __init__(self):
        self.nodes = {}

    def register_node(self, node_id, metadata=None):
        self.nodes[node_id] = metadata or {}

    def available_nodes(self):
        return list(self.nodes.keys())
