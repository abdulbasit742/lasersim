"""Distributed health monitoring foundation for LaserSim nodes."""

class DistributedHealthMonitor:
    def __init__(self):
        self.nodes = {}

    def update_node(self, node_id, status):
        self.nodes[node_id] = status

    def get_health(self):
        return self.nodes
