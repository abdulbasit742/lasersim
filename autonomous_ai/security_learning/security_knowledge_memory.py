"""Security knowledge memory foundation for LaserSim AI."""

class SecurityKnowledgeMemory:
    def __init__(self):
        self.knowledge = []

    def store_pattern(self, pattern):
        self.knowledge.append(pattern)

    def get_patterns(self):
        return list(self.knowledge)
