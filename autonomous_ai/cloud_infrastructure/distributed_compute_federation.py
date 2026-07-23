"""Distributed compute federation foundation for LaserSim AI."""

class DistributedComputeFederation:
    def __init__(self):
        self.compute_nodes = []

    def register_node(self, node):
        self.compute_nodes.append(node)

    def available_nodes(self):
        return self.compute_nodes
