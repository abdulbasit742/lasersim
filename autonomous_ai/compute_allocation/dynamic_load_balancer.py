"""Dynamic load balancing foundation for LaserSim."""

class DynamicLoadBalancer:
    def __init__(self):
        self.nodes = []

    def register_node(self, node):
        self.nodes.append(node)

    def choose_node(self):
        if not self.nodes:
            return None
        return self.nodes[0]
