"""AI contextual awareness system foundation for LaserSim AI."""

class AIContextualAwarenessSystem:
    def __init__(self):
        self.contexts = []

    def add_context(self, context):
        self.contexts.append(context)

    def get_contexts(self):
        return self.contexts
