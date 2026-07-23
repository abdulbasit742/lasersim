"""AI knowledge graph foundation."""

class AIKnowledgeGraphFoundation:
    def __init__(self):
        self.nodes = {}
        self.connections = []

    def add_node(self, key, value):
        self.nodes[key] = value

    def connect(self, source, target):
        self.connections.append((source, target))
