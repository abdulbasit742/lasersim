"""Knowledge base layer for previous LaserSim experiments."""

class KnowledgeBase:
    def __init__(self):
        self.knowledge = {}

    def add_entry(self, key, value):
        self.knowledge[key] = value

    def query(self, key):
        return self.knowledge.get(key)
