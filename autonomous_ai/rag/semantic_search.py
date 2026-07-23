"""Semantic experiment search foundation for LaserSim AI memory."""

class SemanticSearch:
    def __init__(self):
        self.index = []

    def add_memory(self, experiment):
        self.index.append(experiment)

    def search(self, query):
        return [item for item in self.index if query.lower() in str(item).lower()]
